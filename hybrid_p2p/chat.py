import threading, sys, time
from random import randint
from socket import *
# import socket

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
        sThread = threading.Thread(target=self.sendMsg, args=())
        sThread.daemon = True
        sThread.start()

        # TO DO: catch KeyboardInterrupt at blocking method
        while True:
        # while not stop_server_threads:
            with self.condition:
                if stop_server_threads:
                    break
            c, a = sock.accept(timeout=1) # blocking method
            cThread = threading.Thread(target=self.handler, args=(c, a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            self.peers.append(a[0]) # appends IP address
            print(str(a[0]) + ":" + str(a[1]), "connected")
            self.sendPeers()
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
    
    def sendMsg(self, ):
        global stop_server_threads
        while True:
            msg = input("")

            if msg.lower() == 'exit':
                # # might need to perform some cleanup here
                # print('condition met')
                # stop_server_threads = True
                # sys.exit(0)

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

    def sendMsg(self,sock):
        while True:
            sock.send(bytes(input(""), "utf-8")) # blocking function
            sys.stdout.write("\033[F")

    def __init__(self, address):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        sock.connect((address, 10000))
        print("Client running ...")

        # thread to wait for input, send message to server
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
                    print("Couldn't start the server ...")
                    print(e)
    except KeyboardInterrupt:
        sys.exit(0)

# while True:
#     try:
#         print("Trying to connect ...")
#         time.sleep(randint(1,5))

#         if len(p2p.peers) == 0:
#             try:
#                 p2p.peers = [socket.gethostbyname(socket.gethostname())]
#                 print('hostname: ', socket.gethostname())
#                 print('IP: ', socket.gethostbyname(socket.gethostname()))
#                 server = Server()
#             except KeyboardInterrupt:
#                 sys.exit(0)
#             except:
#                 print("Couldn't start the server ...")
#         else:
#             for peer in p2p.peers:
#                 try:
#                     print('number of peers: ', len(p2p.peers))
#                     client = Client(peer)
#                 except KeyboardInterrupt:
#                     sys.exit(0)
#                 except:
#                     pass
#     except KeyboardInterrupt:
#         sys.exit(0)