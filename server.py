import pickle
import socket
from _thread import *

from message import Message

class Server(object):

    def __init__(self, sip, sport, cports):
        self.server_ip = sip
        self.server_port = sport
        self.client_ports_available = cports
        self.client_ports_in_use = []

        self.test = []

        self.welcome_message = "Welcome to the chatroom. "


    def server(self):
        # self.accept_client_connection()

        # self.test_con()


        ServerSocket = socket.socket()
        ThreadCount = 0
        try:
            ServerSocket.bind((self.server_ip, self.server_port))
        except socket.error as e:
            print(str(e))
        ServerSocket.listen(5)

        while True:
            Client, address = ServerSocket.accept()
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            start_new_thread(self.threaded_server, (Client,))
            ThreadCount += 1
            print('Thread Number: ' + str(ThreadCount))
        ServerSocket.close()

    def threaded_server(self, connection):
        connection.send(self.welcome_message.encode('utf-8', 'replace'))
        while True:
            data = connection.recv(2048)
            data = data.decode('utf-8')
            if data == Message.disconnect:
                reply = "Disconnecting"
                connection.sendall(reply.encode('utf-8', 'replace'))
                break
            else:
                reply = 'Server received: ' + data
            if not data:
                break

            connection.sendall(reply.encode('utf-8', 'replace'))
        connection.close()



