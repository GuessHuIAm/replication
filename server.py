import re
import sqlite3
from concurrent import futures
from multiprocessing import Process
from time import sleep

import grpc

import chat_pb2 as pb2
import chat_pb2_grpc as pb2_grpc
from constants import *

# Associates a unique username with a password
accounts = {}

# Associates a username with a logged-in status
accounts_status = {}

# Associates a user with a dictionary storing senders : list of messages
accounts_queue = {}

class ChatService(pb2_grpc.ChatServicer):
    def __init__(self, *args, **kwargs):
        pass


    def CreateAccount(self, request, context):
        '''
        Creates a new account with the given username and password.
        If the username already exists, an error is returned.
        '''
        # Sync with all secondary replicas if necessary
        if is_primary:
            for s in stubs:
                try:
                    s.CreateAccount(request)
                except grpc._channel._InactiveRpcError:
                    pass

        username = request.username
        password = request.password
        if username not in accounts:
            accounts[username] = password
            accounts_status[username] = False
            accounts_queue[username] = {}
            result = f'{username} added'
            response = {'message': result, 'error': False}
        else:
            result = "Error: Username already in use"
            response = {'message': result, 'error': True}

        return pb2.ServerResponse(**response)


    def DeleteAccount(self, request, context):
        '''
        Deletes the account with the given username and password.
        If the username or password is incorrect, an error is returned.
        '''
        # Sync with all secondary replicas if necessary
        if is_primary:
            for s in stubs:
                try:
                    s.DeleteAccount(request)
                except grpc._channel._InactiveRpcError:
                    pass

        username = request.username
        password = request.password
        if username not in accounts:
            result = f'{username} is not an existing username'
            response = {'message': result, 'error': True}
            return pb2.ServerResponse(**response)

        if password != accounts[username]:
            result = f'Wrong password for {username}'
            response = {'message': result, 'error': True}
            return pb2.ServerResponse(**response)

        del(accounts[username])
        result = f'{username} deleted'
        response = {'message': result, 'error': False}
        return pb2.ServerResponse(**response)


    def Login(self, request, context):
        '''
        Once use logs in, server immediately creates a thread for that
        user that is working on user's behalf looking for messages.
        '''
        # Sync with all secondary replicas if necessary
        if is_primary:
            for s in stubs:
                try:
                    s.Login(request)
                except grpc._channel._InactiveRpcError:
                    pass

        username = request.username
        password = request.password

        if username not in accounts:
            result = f'{username} is not a registered account.'
            response = {'message': result, 'error': True}
            return pb2.ServerResponse(**response)

        if password != accounts[username]:
            result = f"Incorrect password for {username}'s account."
            response = {'message': result, 'error': True}
            return pb2.ServerResponse(**response)

        accounts_status[username] = True
        result = f'{username}, you are logged in'
        response = {'message': result, 'error': False}
        return pb2.ServerResponse(**response)


    def Logout(self, request, context):
        '''Logout the client'''
        # Sync with all secondary replicas if necessary
        if is_primary:
            for s in stubs:
                try:
                    s.Logout(request)
                except grpc._channel._InactiveRpcError:
                    pass

        username = request.username
        accounts_status[username] = False
        result = f'{username}, you are logged out'
        response = {'message': result, 'error': False}
        return pb2.ServerResponse(**response)


    def ListAccounts(self, request, context):
        '''Lists the available accounts'''
        searchterm = request.searchterm
        pattern = re.compile(searchterm)
        accounts_str = ""
        for account in accounts:
            if pattern.search(account) != None:
                accounts_str += account + " "
        response = {'usernames': accounts_str[:-1]}
        return pb2.Accounts(**response)


    def SendMessage(self, request, context):
        '''Puts message into the destination user's queue'''
        # Sync with all secondary replicas if necessary
        if is_primary:
            for s in stubs:
                try:
                    s.SendMessage(request)
                except grpc._channel._InactiveRpcError:
                    pass

        destination = request.destination
        source = request.source
        text = request.text

        # If the source is not logged in, return an error
        if source not in accounts or accounts_status[source] == False:
            result = "Error: username not valid or not logged in"
            response = {'message': result, 'error': True}
            return pb2.ServerResponse(**response)

        # If the destination is not a valid account, return an error
        if destination not in accounts:
            result = "Error: destination not valid"
            response = {'message': result, 'error': True}
            return pb2.ServerResponse(**response)

        if source not in accounts_queue[destination]:
            accounts_queue[destination][source] = [text]
        else:
            accounts_queue[destination][source].append(text)
        result = "Message Sent"
        response = {'message': result, 'error': False}

        return pb2.ServerResponse(**response)


    def ListenMessages(self, request, context):
        username = request.username

        while accounts_status[username]:
            myDict = accounts_queue[username]
            for sender in list(myDict):
                for msg in myDict[sender]:
                    response = {'destination': username, 'source': sender, 'text': msg}
                    yield pb2.MessageInfo(**response)
                    myDict[sender].remove(msg)


    def Heartbeat(self, request, context):
        return pb2.NoParam()


def serve(index, server_hierarchy):
    # Flag stating whether the replica is the primary one
    global is_primary
    is_primary = index == 0

    host, port = server_hierarchy[index]
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10)) # 10 threads
    pb2_grpc.add_ChatServicer_to_server(ChatService(), server) # Add service to server
    server.add_insecure_port(f'{host}:{port}')
    server.start()
    print(f'Server started on {host}:{port}' + (' (Replica)' if index > 0 else ''))

    # Define replica stubs for primary to communicate with
    global stubs
    stubs = [
        pb2_grpc.ChatStub(grpc.insecure_channel(f'{host}:{port}'))
        for host, port
        in (server_hierarchy[:index] + server_hierarchy[index + 1:])
    ]

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
    # sleep(15)
    # print('Primary and replica 1 been terminated, duuude')
    # primary.terminate()
    # replica_1.terminate()