import socket
import threading
from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE, SIG_DFL)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
client_socket.bind(('', 8000))
client_socket.listen(5)

index_table = {"1": "10.0.0.1", "2": "10.0.0.2", "3": "10.0.0.3", "4": "10.0.0.4"}

while True:
    c, addr = client_socket.accept()
    c.send(index_table["2"].encode())

client_socket.close()

