import socket
import threading
import select

# Define the protocol
HEADER_SIZE = 10
MSG_TYPES = {
    'CHAT': 0,
    'JOIN': 1,
    'LEAVE': 2
}

# Define the user interface
def prompt():
    return input("> ")

# Define the networking functionality
class Peer:
    def __init__(self, addr, port, chat_port):
        self.addr = addr
        self.port = port
        self.chat_port = chat_port
        
class SuperPeer:
    def __init__(self, port):
        self.port = port
        self.chat_port = port + 1  # new port for incoming chat messages
        self.peers = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.sock.bind(('localhost', self.port))
        self.sock.listen(5)

    def start(self):
        # Start listening for incoming chat messages from peers
        chat_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        chat_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        chat_sock.bind(('localhost', self.chat_port))
        chat_sock.listen(5)

        while True:
            # Check for incoming connections on both sockets
            ready_to_read, _, _ = select.select([self.sock, chat_sock], [], [], 0)
            for sock in ready_to_read:
                if sock == self.sock:
                    conn, addr = self.sock.accept()
                    t = threading.Thread(target=self.handle_peer, args=(conn, addr))
                    t.start()
                elif sock == chat_sock:
                    conn, addr = chat_sock.accept()
                    t = threading.Thread(target=self.handle_chat_peer, args=(conn, addr))
                    t.start()

    def handle_peer(self, conn, addr):
        # Handle JOIN and LEAVE messages as before
        header_bytes = conn.recv(HEADER_SIZE)
        header = int(header_bytes.decode().strip())
        data = conn.recv(header).decode()
        msg_type, *msg_data = data.split("|")

        if msg_type == str(MSG_TYPES['JOIN']):
            peer = Peer(addr[0], int(msg_data[0]), self.chat_port)
            self.peers.append(peer)
        elif msg_type == str(MSG_TYPES['LEAVE']):
            peer = Peer(addr[0], int(msg_data[0]), self.chat_port)
            self.peers.remove(peer)

    def handle_chat_peer(self, conn, addr):
        # Receive chat message from peer and broadcast to other peers
        header_bytes = conn.recv(HEADER_SIZE)
        header = int(header_bytes.decode().strip())
        data = conn.recv(header).decode()
        msg_type, *msg_data = data.split("|")

        if msg_type == MSG_TYPES['CHAT']:
            msg = f"{addr[0]}:{msg_data[0]}"
            for peer in self.peers:
                if peer.addr != addr[0]:
                    peer_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    peer_conn.connect((peer.addr, peer.chat_port))  # use chat_port
                    header = f"{len(msg):<{HEADER_SIZE}}"
                    peer_conn.send(header.encode() + msg.encode())

# class SuperPeer:
    # def __init__(self, port):
    #     self.port = port
    #     self.peers = []
    #     self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    #     self.sock.bind(('localhost', self.port))
    #     self.sock.listen(5)

    # def start(self):
    #     while True:
    #         conn, addr = self.sock.accept()
    #         t = threading.Thread(target=self.handle_peer, args=(conn, addr))
    #         t.start()

    # def handle_peer(self, conn, addr):
    #     # Receive message
    #     header_bytes = conn.recv(HEADER_SIZE)
    #     header = int(header_bytes.decode().strip())
    #     data = conn.recv(header).decode()
    #     msg_type, *msg_data = data.split("|")

    #     # Handle message
    #     if msg_type == MSG_TYPES['JOIN']:
    #         self.handle_join(conn, addr, msg_data)
    #     elif msg_type == MSG_TYPES['LEAVE']:
    #         self.handle_leave(conn, addr, msg_data)
    #     elif msg_type == MSG_TYPES['CHAT']:
    #         self.handle_chat(conn, addr, msg_data)

    def handle_join(self, conn, addr, msg_data):
        peer = Peer(addr[0], int(msg_data[0]))
        self.peers.append(peer)

    def handle_leave(self, conn, addr, msg_data):
        peer = Peer(addr[0], int(msg_data[0]))
        self.peers.remove(peer)

    def handle_chat(self, conn, addr, msg_data):
        msg = f"{addr[0]}:{msg_data[0]}"
        for peer in self.peers:
            if peer.addr != addr[0]:
                peer_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_conn.connect((peer.addr, peer.port))
                header = f"{len(msg):<{HEADER_SIZE}}"
                peer_conn.send(header.encode() + msg.encode())

if __name__ == '__main__':
    # Start super peer
    super_peer = SuperPeer(5000)
    threading.Thread(target=super_peer.start).start()

    # Prompt user to join chat
    print("Welcome to the chat!")
    username = input("Enter your username: ")
    port = int(input("Enter the port you want to use: "))

    # Join chat as a peer
    peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_sock.connect(('localhost', 5000))
    join_msg = f"{MSG_TYPES['JOIN']}|{port}"
    header = f"{len(join_msg):<{HEADER_SIZE}}"
    peer_sock.send(header.encode() + join_msg.encode())

    # Start listening for incoming chat messages
    def receive_messages():
        peer_listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_listen_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        peer_listen_sock.bind(('localhost', port))
        peer_listen_sock.listen(5)
        while True:
            conn, addr = peer_listen_sock.accept()
            header_bytes = conn.recv(HEADER_SIZE)
            header = int(header_bytes.decode().strip())
            data = conn.recv(header).decode()
            print(data)

    threading.Thread(target=receive_messages).start()

    # Send chat messages
    while True:
        message = input()
        if message.lower() == 'exit':
            leave_msg = f"{MSG_TYPES['LEAVE']}|{port}"
            header = f"{len(leave_msg):<{HEADER_SIZE}}"
            peer_sock.send(header.encode() + leave_msg.encode())
            break
        chat_msg = f"{MSG_TYPES['CHAT']}|{username}: {message}"
        header = f"{len(chat_msg):<{HEADER_SIZE}}"
        peer_sock.send(header.encode() + chat_msg.encode())

