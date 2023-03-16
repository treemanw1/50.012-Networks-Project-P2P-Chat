import threading
import socket

class Server:
    def __init__(self, local_port, remote_host, remote_port):
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = 60000
        self.sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_listen.bind(('localhost', self.local_port))
        self.sock_listen.listen(1)
        print(f"Server started on port {self.local_port}")

        self.sock_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock_send.connect((self.remote_host, self.remote_port))
            print(f"Connected to {self.remote_host}:{self.remote_port}")

        except:
            print("error")
       
    def handle_incoming(self):
        while True:
            conn, addr = self.sock_listen.accept()
            print(f"Incoming connection from {addr}")
            threading.Thread(target=self.handle_incoming_client, args=(conn,)).start()

    def handle_incoming_client(self, conn):
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"Received data from client: {data}")
                self.sock_send.sendall(data)

    def start(self):
        threading.Thread(target=self.handle_incoming).start()

if __name__ == '__main__':
    server = Server(local_port=12345, remote_host='localhost', remote_port=12346)
    server.start()
