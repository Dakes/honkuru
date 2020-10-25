import pickle
import socket
# from _thread import *
import _thread
import threading
from time import sleep

from message import Message


class Server(object):

    def __init__(self, sip, sport, cports, verbose=False):
        self.server_ip = sip
        self.server_port = sport
        self.client_ports_available = cports
        # self.client_ports_in_use = []
        self.clients = set()
        self.clients_lock = threading.Lock()

        self.last_message = None
        self.messages = []

        self.verbose = verbose

    def server(self):
        server_socket = socket.socket()
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

        wlc = Message(Message.server_user, Message.welcome_message)
        wlc_pickled = pickle.dumps(wlc)
        connection.send(wlc_pickled)

        while True:
            msg_pickled = connection.recv(4096)

            # skip if string is empty (does not come from client)
            if not msg_pickled:
                sleep(0.01)
                continue

            msg = pickle.loads(msg_pickled)

            # Check for communication Strings, not Message objects
            # disconnect
            if msg_pickled == Message.close_connection:
                with self.clients_lock:
                    self.clients.remove(connection)
                # Notify all clients of leaver
                client_disconnected_msg = Message(Message.server_user, "User '" + msg.user + "' disconnected.")
                self.distribute_message(client_disconnected_msg)
                # send discharge message to client and close connection
                discharge = pickle.dumps(Message(Message.server_user, Message.discharge_msg))
                connection.send(discharge)
                sleep(1)
                break

            self.messages.append(msg)

            # first check for special codes (sent as string instead of Message object)

            print(msg.user + ": " + msg.message)
            self.distribute_message(msg)
            if not msg_pickled:
                break

        connection.close()

    def distribute_message(self, msg):
        """
        Sends the given message to all connected clients
        :param msg:
        """
        msg_pickled = pickle.dumps(msg)
        with self.clients_lock:
            for client in self.clients:
                # print("sending to: ", client)
                client.send(msg_pickled)

