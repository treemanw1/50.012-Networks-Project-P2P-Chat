import socket
import threading
from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE, SIG_DFL)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
client_socket.bind(('', 8000))
client_socket.listen(5)

message = "hi"

while True:
    c, addr = client_socket.accept()
    c.send(message.encode())

client_socket.close()

