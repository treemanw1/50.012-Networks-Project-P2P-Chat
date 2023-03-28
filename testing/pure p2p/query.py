import sys
import socket
import threading
from thread import *
from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE, SIG_DFL)

message = "hi"
address = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]
port = 8000
sockets = []

def threaded(i):
    while True: 
        msg = i.recv(1024)
        if(msg != None):   
           print(msg.decode())
           break
    i.close()

for addr in address:
    client_socket = socket.socket()
    client_socket.connect((addr, port))
    sockets.append(client_socket)

    my_thread = threading.Thread(target=threaded, args=[client_socket])
    my_thread.start()


