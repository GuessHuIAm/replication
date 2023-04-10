import socket

PRIMARY_HOST = socket.gethostbyname(socket.gethostname())  # Default host address for primary
PRIMARY_PORT = 8000        # Default port number for primary
REP_1_HOST = PRIMARY_HOST  # Default port number for replica 1
REP_1_PORT = 8001          # Default host address for replica 1
REP_2_HOST = PRIMARY_HOST  # Default port number for replica 2
REP_2_PORT = 8002          # Default host address for replica 2

ILLEGAL_CHARS = {'.', '+', '*', '?', '^', '$', '(', ')', '[', ']', '{', '}', '|', '\\'}

DB_NAME = 'replication_chat'

DATABASE = {
    'user': 'root',
    #'password': '',
    'database': DB_NAME,
    'host': 'localhost',
}