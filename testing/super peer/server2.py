import socket
import threading
from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE, SIG_DFL)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
client_socket.bind(('', 8000))
client_socket.listen(5)

index_table = {"1": "10.0.0.5", "2": "10.0.0.6", "3": "10.0.0.7", "4": "10.0.0.8"}
port = 8000

def threaded(i, client):
    while True:
        msg = i.recv(1024)
        if (msg != None):
            print(msg.decode())
            client.send(msg)
            break
    i.close()

while True:
    c, addr = client_socket.accept()
    
    # index the resources within its peer group and find 10.0.0.8
    peer_socket_address = index_table["4"]
       
    peer_socket = socket.socket()
    peer_socket.connect((peer_socket_address, port))
    
    my_thread = threading.Thread(target=threaded, args=[peer_socket, c])
    my_thread.start()

client_socket.close()

