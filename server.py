import pickle
import socket
# from _thread import *
import _thread
import threading
from time import sleep

from message import Message

class Server(object):

    def __init__(self, sip, sport, cports):
        self.server_ip = sip
        self.server_port = sport
        self.client_ports_available = cports
        # self.client_ports_in_use = []
        self.clients = set()
        self.clients_lock = threading.Lock()

        self.last_message = None
        self.messages = []


        self.welcome_message = "Welcome to the chatroom. "


    def server(self):
        server_socket = socket.socket()
        thread_count = 0
        try:
            server_socket.bind((self.server_ip, self.server_port))
        except socket.error as e:
            print(str(e))
            exit(1)
        server_socket.listen(5)

        while True:
            client, address = server_socket.accept()
            with self.clients_lock:
                check_msg = client.recv(1024)
                # only add to clients if not a test connect to see if server is available
                if check_msg == Message.check_available:
                    client.send(Message.server_available)
                    client.close()
                    continue
                elif check_msg == Message.client_connection:
                    self.clients.add(client)
                    print('Connected to: ' + address[0] + ':' + str(address[1]))
                    _thread.start_new_thread(self.threaded_server, (client,))
        server_socket.close()

    def threaded_server(self, connection):

        wlc = Message(Message.server_user, self.welcome_message)
        wlc_pickled = pickle.dumps(wlc)
        connection.send(wlc_pickled)

        while True:
            msg_pickled = connection.recv(4096)

            # skip if string is empty (does not come from client)
            if not msg_pickled:
                sleep(0.01)
                continue

            # print("Received data: ", data)
            msg = pickle.loads(msg_pickled)
            self.messages.append(msg)

            # disconnect
            if msg.message == Message.disconnect:
                reply_str = "User '" + msg.user + "' disconnected."
                client_disconnected_msg = Message(Message.server_user, reply_str)
                client_disconnected_msg_pickled = pickle.dumps(client_disconnected_msg)
                self.distribute_message(client_disconnected_msg_pickled)

                discharge = pickle.dumps(Message(Message.server_user, Message.discharge_msg))
                connection.send(discharge)
                break
            else:
                print(msg.user + ": " + msg.message)
                self.distribute_message(msg)
            if not msg_pickled:
                break

        connection.close()

    def distribute_message(self, msg):
        """
        Sends the given message to all connected clients
        :param msg:
        :return:
        """
        with self.clients_lock:
            for client in self.clients:
                # print("sending to: ", client)
                msg_pickled = pickle.dumps(msg)
                client.send(msg_pickled)





