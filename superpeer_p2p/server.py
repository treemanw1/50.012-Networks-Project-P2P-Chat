import socket

HOST = 'localhost'
PORT = 8000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
server_socket.bind((HOST, PORT))
server_socket.listen(10)

clients = []

print('Superpeer server started on {}:{}'.format(HOST, PORT))

while True:
    client_socket, address = server_socket.accept()
    clients.append(client_socket)
    print('Client connected from {}:{}'.format(address[0], address[1]))
    
    # Broadcast the new client's username to other clients
    username = client_socket.recv(1024).decode()
    for client in clients:
        if client != client_socket:
            client.send('{} has joined the chat'.format(username).encode())
    
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                # Broadcast the message to other clients
                for client in clients:
                    if client != client_socket:
                        client.send('{}: {}'.format(username, message).encode())
            else:
                # If the client has disconnected, remove them from the list
                clients.remove(client_socket)
                print('Client disconnected from {}:{}'.format(address[0], address[1]))
                break
        except:
            # If there's an error, assume the client has disconnected
            clients.remove(client_socket)
            print('Client disconnected from {}:{}'.format(address[0], address[1]))
            break
