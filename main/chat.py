# See https://www.youtube.com/watch?v=Rvfs6Xx3Kww for more info
# HOW TO RUN 
# In the terminal, type "python3 chat.py"
# Open other terminals, type "python3 chat.py"
# One of them will become the server. If the server is closed, one of the clients will act as a server instead.
# Area of improvements: 
# 1. When the client becomes a server, cannot send message anymore.
# 2. For now, to prevent multiple servers exist at the same time, one client becomes randomly selected to become a server.
# 3. When a client send a message, he will see his message twice.

import threading, sys,time
from random import randint
from socket import *


class Server:
    
    connections = []
    peers = []

    def __init__(self):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        sock.bind(("0.0.0.0", 10000))
        sock.listen(1)
        print("Server running ...")
        while True:
            c, a = sock.accept() # blocking method
            cThread = threading.Thread(target=self.handler, args=(c, a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            self.peers.append(a[0]) # appends IP address
            print(str(a[0]) + ":" + str(a[1]), "connected")
            self.sendPeers()

    def handler(self, c, a):
        while True:
            data = c.recv(1024)
            for connection in self.connections:
                connection.send(data)
            if not data:
                print(str(a[0]) + ":" + str(a[1]), "disconnected")
                self.connections.remove(c)
                self.peers.remove(a[0])
                c.close()
                self.sendPeers()
                break
    def sendPeers(self):
        p=""
        for peer in self.peers:
            p=p+peer+","
        for connection in self.connections:
            connection.send(b'\x11'+bytes(p,'utf-8'))

class Client:

    def sendMsg(self,sock):
        while True:
            sock.send(bytes(input(""), "utf-8"))
            sys.stdout.write("\033[F")

    def __init__(self, address):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        sock.connect((address, 10000))
        print("Client running ...")

        iThread = threading.Thread(target=self.sendMsg, args=(sock,))
        iThread.daemon = True
        iThread.start()

        while True:
            data = sock.recv(1024)
            if not data:
                break
            if data[0:1]==b'\x11':
                self.updatePeers(data[1:])
            else:
                print(str(data, "utf-8"))
    def updatePeers(self, peerData):
        p2p.peers = str(peerData,"utf-8").split(",")[:-1]

class p2p:
    peers =['127.0.0.1']

# if len(sys.argv) > 1:
#     client = Client(sys.argv[1])
# else:
#     server = Server()
while True:
    try:
        print("Trying to connect ...")
        time.sleep(randint(1,5))
        for peer in p2p.peers:
            try:
                client = Client(peer)
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                pass
            # Temp solution
            # To prevent every one to become a server if not run same computer
            if randint(1,5) == 1:
                try:
                    server = Server()
                except KeyboardInterrupt:
                    sys.exit(0)
                except Exception as e:
                    print(e)
                    print("Couldn't start the server ...")
    except KeyboardInterrupt:
        sys.exit(0)