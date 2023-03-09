import socket
import threading

HOST = 'localhost'
PORT = 8000

username = input('Enter your username: ')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
client_socket.connect((HOST, PORT))
client_socket.send(username.encode())

def receive():
    while True:
        try:
            message = client_socket.recv(1024).decode()
            print(message)
        except:
            # If there's an error, assume the server has disconnected
            client_socket.close()
            break

def send():
    while True:
        message = input('')
        client_socket.send(message.encode())

receive_thread = threading.Thread(target=receive)
send_thread = threading.Thread(target=send)

receive_thread.start()
send_thread.start()
