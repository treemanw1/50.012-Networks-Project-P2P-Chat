import threading, sys, time
from random import randint
from socket import *

stop_threads = False

class SuperPeer:

    def __init__(self):
        self.peers = []

        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", 10000))
        sock.listen(1)
        print("Super Peer running ...")

        while True:
            if stop_threads:
                break
            c, a = sock.accept()  # blocking method
            self.peers.append(a[0])
            print(str(a[0]) + ":" + str(a[1]), "connected to Super Peer")
            self.sendPeers(c)

    def sendPeers(self, c):
        p = ",".join(self.peers)
        c.send(bytes(p, "utf-8"))
        c.close()

stop_server_threads = False

class Server:
    
    connections = []
    peers = []

    def __init__(self):
        self.condition = threading.Condition()

        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)
        sock.bind(("0.0.0.0", 10000))
        sock.listen(1)
        print("Server running ...")

        # Thread waiting for input to send to all connected clients
        sThread = threading.Thread(target=self.sendMsg, args=(sock,))
        sThread.daemon = True
        sThread.start()

        # TO DO: catch KeyboardInterrupt at blocking method
        while True:
        # while not stop_server_threads:
            with self.condition:
                if stop_server_threads:
                    break
            c, a = sock.accept() # blocking method
            cThread = threading.Thread(target=self.handler, args=(c, a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            self.peers.append(a[0]) # appends IP address
            print(str(a[0]) + ":" + str(a[1]), "connected")
            self.sendPeersToSuperPeer(a[0])  # send the new peer's IP to the super peer
            self.sendPeers()  # send the updated list of peers to all connected clients
        print('MAIN END')

    def handler(self, c, a):
        while True:
            data = c.recv(1024) # blocking method
            if data: print(str(data, "utf-8"))
            with self.condition:
                if stop_server_threads:
                    break

            for connection in self.connections:
                connection.send(data)
            if not data:
                print(str(a[0]) + ":" + str(a[1]), "disconnected")
                self.connections.remove(c)
                self.peers.remove(a[0])
                c.close()
                self.sendPeers()
                break
        print('HANDLER END')
    
    def sendMsg(self, sock):
        global stop_server_threads
        while True:
            try:
                msg = input("")
            except:
                print("\nKeyboardInterrupt detected. Closing connection.")
                sock.close()
                break
            if msg.lower() == 'exit':
                with self.condition:
                    global stop_server_threads
                    stop_server_threads = True
                    self.condition.notify_all()
                break
            data = bytes(msg, "utf-8")
            for connection in self.connections:
                connection.send(data)
        print('SENDMSG END')

    def sendPeers(self):
        if not stop_server_threads:
            p=""
            for peer in self.peers:
                p=p+peer+","
            for connection in self.connections:
                connection.send(b'\x11'+bytes(p,'utf-8'))

   



class Client:

    def sendMsg(self, sock):
        while True:
            try:
                msg = input("")
                if msg.lower() == 'exit':
                    sock.close()
                    break
                data = bytes(msg, "utf-8")
                for connection in self.connections:
                    connection.send(data)
            except:
                print("\nKeyboardInterrupt detected. Closing connection.")
                sock.close()
                break

    def listener(self, sock):
        while True:
            try:
                data = sock.recv(1024)
                if not data:
                    break
                print(str(data, "utf-8"))
            except:
                print("\nKeyboardInterrupt detected. Closing connection.")
                sock.close()
                break

    def __init__(self, peers):
        self.connections = []

        for peer in peers:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            try:
                sock.connect((peer, 10000))
                self.connections.append(sock)
                print("Connected to " + peer)
            except:
                print("Could not connect to " + peer)

        # thread to wait for input, send message to all peers
        iThread = threading.Thread(target=self.sendMsg, args=(sock,))
        iThread.daemon = True
        iThread.start()

        # thread to listen for incoming messages from other peers
        lThread = threading.Thread(target=self.listener, args=(sock,))
        lThread.daemon = True
        lThread.start()

