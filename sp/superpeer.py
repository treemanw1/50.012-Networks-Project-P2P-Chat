# edits on superpeer:
# whoever starts first wiill become a "superpeer"
# the ratio of superpeer to peers is 1:2
# port for server must always be unique and starts from 60000 to ensure always empty port
# when server closes unexpectedly, the peer becomes superpeer sequentially
# sendtrack()
# is_port_in_used()
# prompt "client disconnected" at the proper place in main while loop
#
#  Areas of improvement:
# superpeers needs to connect to other superpeers
# change sequential promotion of peer to superpeers to be based on processing power instead (or some metrics)
#
# THINGS TO NOTE:
# "EXCEPT: PASS" BYPASSES ALL ERRORS, THEREFORE WHEN DEBUGGING/CODING, MIGHT WANT TO REMOVE IT TO ALLOW CATCHING OF ERRORS


import threading
import sys
import time
from random import randint
from socket import *

stop_server_threads = False
presentpeers = []  # take into account how many peers after current client
serverls = []


class Server:

    connections = []
    peers = []
    ipAndPort = []

    def __init__(self):
        self.condition = threading.Condition()

        sock = socket(AF_INET, SOCK_STREAM)
        # sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        for i in range(60000, 65535):
            try:
                sock.bind(("0.0.0.0", i))
                break
            except:
                print(f"cannot bind port at {i}")
        print(sock.getsockname())
        sock.listen(1)
        print("Server running ...")
        # global serverls
        # serverls.append()
        # print(serverls)

        # Thread waiting for input to send to all connected clients
        sThread = threading.Thread(target=self.sendMsg, args=(sock,))
        sThread.daemon = True
        sThread.start()

        while True:
            # while not stop_server_threads:
            with self.condition:
                if stop_server_threads:
                    break
            c, a = sock.accept()  # blocking method
            cThread = threading.Thread(target=self.handler, args=(c, a))
            cThread.daemon = True
            cThread.start()
            if len(self.connections) == 2:
                c.close()
            self.connections.append(c)
            self.peers.append(a[0])  # appends IP address
            self.ipAndPort.append(str(a[0]) + ":" + str(a[1]))
            print(self.ipAndPort)
            print(str(a[0]) + ":" + str(a[1]), "connected")
            self.sendtrack()
            # self.sendPeers() # unless not localhost
        print('MAIN END')

    # send ip and port to peer with unique header to filter recv data
    def sendtrack(self):
        if not stop_server_threads:
            data = str(self.ipAndPort)
            self.connections[-1].send(b'\x10'+bytes(data, 'utf-8'))

    def handler(self, c, a):
        while True:
            data = c.recv(1024)  # blocking method
            if data:
                print(str(data, "utf-8"))
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
            p = ""
            for peer in self.peers:
                p = p+peer+","
            for connection in self.connections:
                connection.send(b'\x11'+bytes(p, 'utf-8'))


class Client:

    def is_port_in_use(self, port):
        with socket(AF_INET, SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
            except OSError:
                return True
            else:
                return False

    def sendMsg(self, sock):
        while True:
            try:
                sock.send(bytes(input(""), "utf-8"))  # blocking function
                sys.stdout.write("\033[F")
            except:
                print("\nKeyboardInterrupt detected. Closing connection.")
                sock.close()
                break

    def __init__(self, address):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        for i in range(60000, 65535):
            bool = self.is_port_in_use(i)
            print("bool: ", bool)
            if bool:
                sock.connect((address, i))
                print("Client running ...")
                break
            else:
                print(f"cannot connect to server at port {i}")

        # thread to wait for input, send message to server
        iThread = threading.Thread(target=self.sendMsg, args=(sock,))
        iThread.daemon = True
        iThread.start()

        while True:
            data = sock.recv(1024)
            # print("data: ", str(data, "utf-8"))
            if not data:
                print("not data")
                break
            if data[0:1] == b'\x11':
                self.updatePeers(data[1:])
                print("x11: ", data[1:])
            elif data[0:1] == b'\x10':
                print("yay")
                global presentpeers
                presentpeers = str(
                    data[3:-2], 'utf-8').replace("'", "").replace(" ", "").split(',')
                print(presentpeers)
            else:
                print("else case: ", str(data, "utf-8"))

        print("outside client init while loop")

    def updatePeers(self, peerData):
        p2p.peers = str(peerData, "utf-8").split(",")[:-1]


class p2p:
    peers = ['127.0.0.1']


while True:
    try:
        print("Trying to connect ...")
        time.sleep(randint(1, 3))
        for peer in p2p.peers:
            try:
                client = Client(peer)
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                pass
            print("client disconnected")

            try:
                presentpeers.pop(0)
            except:
                pass

            if len(presentpeers) == 0:

                # Temp solution
                # To prevent every one to become a server if not run same computer
                # if randint(1, 3) == 1:
                try:
                    server = Server()
                except KeyboardInterrupt:
                    sys.exit(0)
                except Exception as e:
                    print("Couldn't start the server ...")
                    print(e)
    except KeyboardInterrupt:
        sys.exit(0)
