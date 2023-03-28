import sys
import socket
import threading
from thread import *
from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE, SIG_DFL)

message = "hi"
server_address = "10.0.0.1"
port = 8000

def threaded(i):
    def peer_thread(peer):
        while True:
            msg = peer.recv(1024)
            if (msg != None):
                print(msg)
                break
        peer.close()

    while True: 
        msg = i.recv(1024)
        if(msg != None): 
           peer_address = msg.decode()  
           print(peer_address)
           
           peer_socket = socket.socket()
           peer_socket.connect((peer_address, port))
           
           peer_thread = threading.Thread(target=peer_thread, args=[peer_socket])
           peer_thread.start()
           break
    i.close()

client_socket = socket.socket()
client_socket.connect((server_address, port))

my_thread = threading.Thread(target=threaded, args=[client_socket])
my_thread.start()


