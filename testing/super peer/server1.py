import socket
import threading
from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE, SIG_DFL)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
client_socket.bind(('', 8000))
client_socket.listen(5)

index_table = {"1": "10.0.0.1", "2": "10.0.0.2", "3": "10.0.0.3", "4": "10.0.0.4"}
neighbour_super_peer_address = "10.0.0.5"
port = 8000

def threaded(i, client):
    while True:
        msg = i.recv(1024)
        if (msg != None):
            print(msg.decode())
            client.send(msg)
            break
    i.close()

print("begin")
while True:
    c, addr = client_socket.accept()

    if ("5" not in index_table):   
        super_peer_socket = socket.socket()
        super_peer_socket.connect((neighbour_super_peer_address, port))
        my_thread = threading.Thread(target=threaded, args=[super_peer_socket, c])
        my_thread.start()        

client_socket.close()

