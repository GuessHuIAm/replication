import re
import mysql.connector
from concurrent import futures
from multiprocessing import Process
from threading import Thread
from time import sleep

import grpc

import chat_pb2 as pb2
import chat_pb2_grpc as pb2_grpc
from constants import *

accounts_status = {}

class ChatService(pb2_grpc.ChatServicer):
    def __init__(self, *args, **kwargs):
        # Add database and link it to this server
        self.conn = mysql.connector.connect(**DATABASE)
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts
                          (username VARCHAR(255) UNIQUE, password VARCHAR(255), status INT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS history
                          (source VARCHAR(255), destination VARCHAR(255), message TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages
                          (source VARCHAR(255), destination VARCHAR(255), message TEXT)''')
        self.conn.commit()
        cursor.close()

    def CreateAccount(self, request, context):
        '''
        Creates a new account with the given username and password.
        If the username already exists, an error is returned.
        '''
        # Sync with all secondary replicas if necessary
        if primary_index == index:
            for s in STUBS[index + 1:]:
                try:
                    s.CreateAccount(request)
                except grpc._channel._InactiveRpcError:
                    pass

        username = request.username
        password = request.password

        cursor = self.conn.cursor()

        # Try to insert the new account into the database, if it already exists, return an error
        try:
            cursor.execute('''INSERT INTO accounts VALUES (%s, %s, %s)''', (username, password, 0))
            self.conn.commit()
            result = f"Account creation success: '{username}' added."
            response = {'message': result, 'error': False}
        except:
            result = f"Account creation error: username '{username}' already in use."
            response = {'message': result, 'error': True}

        cursor.close()

        return pb2.ServerResponse(**response)


    def DeleteAccount(self, request, context):
        '''
        Deletes the account with the given username and password.
        If the username or password is incorrect, an error is returned.
        '''
        # Sync with all secondary replicas if necessary
        if primary_index == index:
            for s in STUBS[index + 1:]:
                try:
                    s.DeleteAccount(request)
                except grpc._channel._InactiveRpcError:
                    pass

        username = request.username
        password = request.password

        cursor = self.conn.cursor()

        try:
            cursor.execute('''DELETE FROM accounts WHERE username = %s AND password = %s''', (username, password,))
            deleted = cursor.rowcount
            self.conn.commit()

            # If the account was deleted, return a success message
            if deleted > 0:
                result = f"Account deletion success: '{username}' deleted."
                response = {'message': result, 'error': False}
            else:
                # If number of rows deleted is 0, then the username was incorrect
                result = f"Account deletion error: username '{username}' not found."
                response = {'message': result, 'error': True}
        except:
            # If the password was incorrect, an exception will be raised
            result = f"Account deletion error: username '{username}' not found."
            response = {'message': result, 'error': True}

        cursor.close()

        return pb2.ServerResponse(**response)


    def Login(self, request, context):
        '''
        Once use logs in, server immediately creates a thread for that
        user that is working on user's behalf looking for messages.
        '''
        # Sync with all secondary replicas if necessary
        if primary_index == index:
            for s in STUBS[index + 1:]:
                try:
                    s.Login(request)
                except grpc._channel._InactiveRpcError:
                    pass

        username = request.username
        password = request.password

        cursor = self.conn.cursor()

        # Find the account with the given username
        cursor.execute('''SELECT * FROM accounts WHERE username = %s''', (username,))
        account = cursor.fetchone()

        if account:
            # If the account exists, check if the password is correct
            if password != account[1]:
                result = f"Login error: incorrect password for '{username}'."
                response = {'message': result, 'error': True}
            else:
                try:
                    cursor.execute('''UPDATE accounts SET status = 1 WHERE username = %s''', (username,))
                    self.conn.commit()
                    result = f"Login success: '{username}' logged in. Welcome!"
                    response = {'message': result, 'error': False}
                except:
                    result = f"Login error: '{username}' is already logged in. Please logout first."
                    response = {'message': result, 'error': True}
        else:
            result = f"Login error: username '{username}' not found."
            response = {'message': result, 'error': True}

        cursor.close()

        return pb2.ServerResponse(**response)


    def Logout(self, request, context):
        '''Logout the client'''
        # Sync with all secondary replicas if necessary
        if primary_index == index:
            for s in STUBS[index + 1:]:
                try:
                    s.Logout(request)
                except grpc._channel._InactiveRpcError:
                    pass

        username = request.username
        cursor = self.conn.cursor()

        try:
            # Set the status of the account to 0 (logged out)
            cursor.execute("UPDATE accounts SET status = 0 WHERE username = %s", (username,))
            self.conn.commit()
            result = f"Logout success: '{username}' logged out. Goodbye!"
            response = {'message': result, 'error': False}
        except:
            result = f"Logout error: something went wrong, please try again."
            response = {'message': result, 'error': True}

        cursor.close()

        return pb2.ServerResponse(**response)


    def ListAccounts(self, request, context):
        '''Lists the available accounts'''
        searchterm = request.searchterm
        pattern = re.compile(searchterm)

        cursor = self.conn.cursor()
        cursor.execute("SELECT username FROM accounts")
        results = cursor.fetchall()
        cursor.close()

        accounts = [r[0] for r in results]
        accounts_str = ""
        for account in accounts:
            if pattern.search(account) is not None:
                accounts_str += account + " "

        response = {'usernames': accounts_str[:-1]}

        return pb2.Accounts(**response)


    def SendMessage(self, request, context):
        '''Puts message into the destination user's queue'''
        # Sync with all secondary replicas if necessary
        if primary_index == index:
            for s in STUBS[index + 1:]:
                try:
                    s.SendMessage(request)
                except grpc._channel._InactiveRpcError:
                    pass

        destination = request.destination
        source = request.source
        text = request.text

        cursor = self.conn.cursor()
        cursor.execute("SELECT status FROM accounts WHERE username = %s", (source,))
        logged_in = cursor.fetchone()[0]

        # If the source is not logged in, return an error
        if logged_in == 0:
            result = "Send error: you must be logged in to send messages."
            response = {'message': result, 'error': True}
            return pb2.ServerResponse(**response)

        # If the destination is not a valid account, return an error
        cursor.execute("SELECT username FROM accounts WHERE username = %s", (destination,))
        if cursor.fetchone() is None:
            result = f"Send error: destination account '{destination}' does not exist."
            response = {'message': result, 'error': True}
            return pb2.ServerResponse(**response)

        try:
            # Add the message to the destination user's queue
            cursor.execute("INSERT INTO messages VALUES (%s, %s, %s)", (destination, source, text,))
            self.conn.commit()
            result = f"Send success: message sent to '{destination}'."
            response = {'message': result, 'error': False}
        except:
            result = "Send error: something went wrong, please try again."
            response = {'message': result, 'error': True}

        cursor.close()

        return pb2.ServerResponse(**response)


    def ListenMessages(self, request, context):
        username = request.username

        cursor = self.conn.cursor()
        while True:
            cursor.execute("SELECT status FROM accounts WHERE username = %s", (username,))
            logged_in = cursor.fetchone()[0]
            if logged_in == 0:
                break

            cursor.execute("SELECT source, text FROM messages WHERE destination = %s", (username,))
            for row in cursor.fetchall():
                source = row[0]
                text = row[1]
                response = {'source': source, 'text': text}
                yield pb2.Message(**response)

            cursor.execute("DELETE FROM messages WHERE receiver = %s AND source = %s AND text = %s", (username, source, text,))
            self.conn.commit()

        cursor.close()


    def Heartbeat(self, request, context):
        return pb2.NoParam()


def heartbeat_primary():
    """
    Function that pings primary replica and determines whether it is still
    functioning. If the primary is no longer functional, the next lowest-indexed
    replica that responds is selected.
    """
    global primary_index
    while primary_index < index:
        try:
            STUBS[primary_index].Heartbeat(pb2.NoParam())
        except grpc._channel._InactiveRpcError:
            primary_index += 1

    # If a replica exits the loop, we know that it has become the primary replica
    print(f'Replica {index} is now the primary replica')


def serve(i, server_hierarchy):
    # Index of the primary replica (initialized to 0)
    global primary_index
    primary_index = 0

    # Index of this process
    global index
    index = i

    # Set up server infra
    host, port = server_hierarchy[index]
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10)) # 10 threads
    pb2_grpc.add_ChatServicer_to_server(ChatService(), server) # Add service to server
    server.add_insecure_port(f'{host}:{port}')
    server.start()
    print(f'Server started on host {host} and port {port}' + (' (Replica)' if index > 0 else ''))

    # Define replica stubs for primary to communicate with
    global STUBS
    STUBS = [
        pb2_grpc.ChatStub(grpc.insecure_channel(f'{host}:{port}'))
        for host, port in server_hierarchy
    ]

    # Start heartbeat with primary replica
    heartbeat_thread = Thread(target=heartbeat_primary, args=())
    heartbeat_thread.start()

    # Server waits for termination
    server.wait_for_termination()


if __name__ == '__main__':
    SERVER_HIERARCHY = [
        (PRIMARY_HOST, PRIMARY_PORT),
        (REP_1_HOST, REP_1_PORT),
        (REP_2_HOST, REP_2_PORT)
    ]

    primary = Process(target=serve, args=(0, SERVER_HIERARCHY))
    replica_1 = Process(target=serve, args=(1, SERVER_HIERARCHY))
    replica_2 = Process(target=serve, args=(2, SERVER_HIERARCHY))

    primary.start()
    replica_1.start()
    replica_2.start()

    # Uncomment below to test swapping between replicas
    # sleep(10)
    # print('Primary and replica 1 been terminated, duuude')
    # primary.terminate()
    # replica_1.terminate()