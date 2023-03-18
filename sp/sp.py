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

# 17/3/2023
# Added listening socket to class Server and put the handler thread properly so connection is filtered out first before the thread is running
# Whats done :
# 1. 2 server can connect to each other
# 2. Now its possible to have superpeer A connected to 2 clients and superpeer B connected to 2 other clients and A and B are connected
# THINGS TO NOTE:
# Ensure connection is not closed before sending data

import threading
import sys
import time
from random import randint
from socket import *

stop_server_threads = False
presentpeers = []  # take into account how many peers after current client
serverls = []

# Must bind between 60000 <= listening port no <= 61000
# Must bind between 61001 <= CONNECTING port no <= 62000
class Server:

    connections = [] # Store connection / socket object of peers
    peers = [] # Store ip address of peers
    ipAndPort = [] # Store ip and Port of connected peers for possible promotion if the superpeer crashes
    othersuperpeersport = [] # Store port of other super peer
    othersuperpeerssocket = [] # Store socket object / connection of other super peer

    client_counter = 0 # Counter to keep track how many clients are connected to current superpeer

    def __init__(self):
        self.condition = threading.Condition()

        sock = socket(AF_INET, SOCK_STREAM) # Socket to listen for incoming request ( acts as a server )
        connecting_sock = socket(AF_INET, SOCK_STREAM) # Socket to connect to other super peer ( to relay / send data )

        # starting from port 60000, try to bind to free port
        for i in range(60000, 61000):
            try:
                sock.bind(("127.0.0.1", i))
                print(f'listening socket is succesfully binded at {i} \n')
                break
            except:
                print(f"cannot bind port at {i}")
        currentPort = sock.getsockname()
        print(f"current port is {currentPort}")
        sock.listen(1)

        # bind connecting socket from 61001 to 62000
        for j in range(61001, 62000):
            try:
                connecting_sock.bind(("0.0.0.0", j))
                print(f'connecting socket is succesfully binded at {j} \n')
                break
            except:
                print(f"cannot bind port at {j}")
        try:
            connecting_sock.connect(('127.0.0.1', int(currentPort[1])-1)) # TODO : now only server 2 connects to server 1 and not both ways
        except WindowsError:
            pass
        print(f"Server running ... with listening socket {currentPort} and connecting socket {connecting_sock.getsockname()}")

        # Thread waiting for input to send to all connected clients
        # args require (var,) to recognise correct type
        sThread = threading.Thread(target=self.sendMsg, args=(sock,))
        sThread.daemon = True
        sThread.start()

        # sendMsgSuperpeerThread = threading.Thread(target=self.sendsuperpeerMsg)
        # sendMsgSuperpeerThread.daemon = True
        # sendMsgSuperpeerThread.start()

        while True:
            # while not stop_server_threads:
            with self.condition:
                if stop_server_threads:
                    break
            # c - connection, a - ip address
            c, a = sock.accept()  # blocking method
            print(f"\nSocket accept c : {c} and a : {a}")
            
            print("ine 90")
            incoming_socket = a[1]
            print("ine 92")
            
            # Check if the incoming connection is Client
            if incoming_socket > 62000:
                print("ine 95")
                # Auto kick client if no of client connected to current super peer is already 2
                if self.client_counter + 1 > 2:
                    print("before close")
                    c.close()
                    print("after close")
                
                else:
                    print("ine 102")
                    self.connections.append(c)  # append connection
                    self.peers.append(a[0])  # appends IP address

                    cThread = threading.Thread(target=self.handler, args=(c, a))
                    cThread.daemon = True
                    cThread.start()

                    # record down number of connections so far, for sequential promotion of superpeer
                    self.ipAndPort.append(str(a[0]) + ":" + str(a[1]))
                    print(self.ipAndPort)
                    print(str(a[0]) + ":" + str(a[1]), "connected")
                    self.sendtrack()
                    
                self.client_counter += 1

            # Check if the incoming connection is other Super Peer
            if 61001 <= incoming_socket <= 62000:
                print(f"other super peer is connected here with socket {incoming_socket}")
                self.othersuperpeerssocket.append(c) # append connection of other superpeer
                self.othersuperpeersport.append(a[1]) # appends port of other superpeer
                print("before super peer thread")
                superpeerThread = threading.Thread(target=self.superpeerhandler, args=(c, a))
                superpeerThread.daemon = True
                superpeerThread.start()
                print("after super peer thread")

            # self.sendPeers() # uncomment if not localhost
        print('MAIN END')

    #  for communicating with other superpeer
    def superpeerhandler(self, c, a):
        print("Super peer handler thread starts")
        c.settimeout(5)

        while True:
            data = bytes([])
            print("before if not")
            if not isinstance(c, socket):
                return 
            print("before try")
            try:
                data = c.recv(1024)  # blocking method
            except timeout:
                print("Socket timed out while receiving data")
                pass
            except:
                print("except data" + str(data, "utf-8"))
                pass
            print("after except")
            if data:
                print(str(data, "utf-8"))
            with self.condition:
                if stop_server_threads:
                    break
            print("before connection")
            for connection in self.othersuperpeerssocket:
                connection.send(data)
            if not data:
                print("superpeer " + str(a[0]) + ":" + str(a[1]), "disconnected")
                # self.othersuperpeerssocket.remove(c)
                # self.othersuperpeersport.remove(a[1])
                
                # c.close()
                # break
        print('Super peer HANDLER END')

    # for sending msg to other super peer
    # def sendsuperpeerMsg(self):
        # global stop_server_threads
        # print('SUPER PEER SENDMSG STARTS')
        # while True:
        #     try:
        #         msg = input("")
        #     except KeyboardInterrupt:
        #         print("\nKeyboardInterrupt detected. Closing connection.")
        #         break

        #     except Exception as e:
        #         print(e)

        #     if msg.lower() == 'exit':
        #         # # might need to perform some cleanup here
        #         # print('condition met')
        #         # stop_server_threads = True
        #         # sys.exit(0)

        #         with self.condition:
        #             global stop_server_threads
        #             stop_server_threads = True
        #             self.condition.notify_all()
        #         break
        #     data = bytes(msg, "utf-8")
        #     print('BEFORE CONNECTION IN SEND SUPERPEERMSG')
        #     for connection in self.othersuperpeerssocket:
        #         connection.send(data)
        # print('SUPER PEER SENDMSG END')

    # send ip and port to peer with unique header to filter recv data
    def sendtrack(self):
        if not stop_server_threads:
            data = str(self.ipAndPort)
            self.connections[-1].send(b'\x10'+bytes(data, 'utf-8'))

    # for communicating with every other peers
    def handler(self, c, a):
        while True:
            data = bytes([])
            if not isinstance(c, socket):
                return 
            try:
                data = c.recv(1024)  # blocking method
            except:
                pass
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
                self.client_counter -= 1
                c.close()
                self.sendPeers()
                break
        print('HANDLER END')

    def sendMsg(self, sock):
        global stop_server_threads
        while True:
            try:
                msg = input("")
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt detected. Closing connection.")
                sock.close()
                break
            except Exception as e:
                print(e)

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
            for superconnection in self.othersuperpeerssocket:
                print(str(superconnection))
                superconnection.send(data)

        print('SENDMSG END')

    def sendPeers(self):

        if not stop_server_threads:
            p = ""
            for peer in self.peers:
                p = p+peer+","
            for connection in self.connections:
                connection.send(b'\x11'+bytes(p, 'utf-8')) 

class Client:
    # check if port is connected/used
    def is_port_in_use(self, port):
        with socket(AF_INET, SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
            except OSError:
                return True
            else:
                return False

    def sendMsg(self, sock):
        while True:
            try:
                sock.send(bytes(input(""), "utf-8"))  # blocking function
                sys.stdout.write("\033[F")
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt detected. Closing connection.")
                sock.close()
                break
            except Exception as e:
                print(f'Client error : {e}') # TODO : Only first Msg on the server doesnt get sent cos of this 
                sock.close()
                break
                

    def __init__(self, address):
        # Client Socket must be binded to 62001 <= socket <= 65535
        sock = socket(AF_INET, SOCK_STREAM)
        # sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        for j in range(62001, 65535):
            try:
                sock.bind(("127.0.0.1", j))
                print(f'Client socket is succesfully binded at {j} \n')
                break
            except:
                print(f"Client cannot bind port at {j}")
        currentPort = sock.getsockname()
        print(f"sock fileno : {sock.fileno()}")
        # if sock.fileno() != -1:
        #     print(f" socket is connected to : {sock.getpeername()}")

        # Try to connect to possible available super peer
        for i in range(60000, 60003):
            # bool = self.is_port_in_use(i)
            # if bool:
            try:
                print(f"Trying to connect to {i} ...")
                sock.connect(('127.0.0.1', i))
                print(f"Client running ... with {address}:{i}")
                
                # Check if the superpeer rejects the client 
                data = sock.recv(1024)
                if not data:
                    print("Server forcibly closed connection with the client")
                    sock.close()
                    sock = socket(AF_INET, SOCK_STREAM)
                    sock.bind(("127.0.0.1", int(currentPort[1])))
                    continue
                else:
                    break
                
            except ConnectionResetError:
                print('The connection was forcibly closed by the server')
            
            except Exception as e:
                print(e)
                print(f"Connection to {i} failed")
                continue
            # else:
            #     print(f"cannot connect to server at port {i}")

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
            # header bit filter to upfate peers
            if data[0:1] == b'\x11':
                self.updatePeers(data[1:])
                print("x11: ", data[1:])
            # header bit filter to update presentpeers
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
            except Exception as e:
                print(e)
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
