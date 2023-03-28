import sys
import socket
import threading
from thread import *
from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE, SIG_DFL)

server_address = "10.0.0.1"
port = 8000

def threaded(i):
    while True:
        msg = i.recv(1024)
        if (msg != None):
            print(msg.decode())
            break
    i.close()

          
client_socket = socket.socket()
client_socket.connect((server_address, port))

my_thread = threading.Thread(target=threaded, args=[client_socket])
my_thread.start()


