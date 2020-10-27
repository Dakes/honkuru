import pickle
import socket
# from _thread import *
import _thread
import threading
from time import sleep

from message import Message


class Server(object):

    def __init__(self, sip, sport, client=None, verbose=False):
        self.server_ip = sip
        self.server_port = sport

        # The client, that ot started in the same session as the server
        self.client = client

        # self.client_ports_in_use = []
        # List of all clients, gets synchronized to all clients. Determines what client will become the next server.
        self.clients = []
        self.clients_lock = threading.Lock()

        self.last_message = None
        self.messages = []

        self.verbose = verbose
        # verbose print function
        self.vprint = print if self.verbose else lambda *a, **k: None

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
                    self.clients.append(client)
                    self.vprint('Connected to: ' + address[0] + ':' + str(address[1]))
                    self.distribute_clients()
                    _thread.start_new_thread(self.threaded_server, (client,))
        server_socket.close()

    def threaded_server(self, connection):

        wlc = Message(Message.server_user, Message.welcome_message)
        wlc_pickled = pickle.dumps(wlc)
        connection.send(wlc_pickled)

        user = None

        recv_empty_counter = 0

        while True:
            print(connection.getpeername()[0])
            print(connection.getpeername()[1])
            msg_pickled = connection.recv(4096)

            # skip if string is empty (does not come from client)
            if not msg_pickled:
                recv_empty_counter = recv_empty_counter + 1
                sleep(0.01)
                # close connection if connection is down
                if recv_empty_counter > 1000000:
                    break
                else:
                    continue

            else:
                recv_empty_counter = 0

            # first check for special codes (sent as string instead of Message object)
            # disconnect
            if msg_pickled == Message.close_connection:
                with self.clients_lock:
                    self.clients.remove(connection)
                # Notify all clients of leaver
                if user is None:
                    user = Message.anonymous_user
                client_disconnected_msg = Message(Message.server_user, "'" + user + "' left the chat.")
                self.distribute_message(client_disconnected_msg)
                # send discharge message to client and close connection
                discharge = pickle.dumps(Message(Message.server_user, Message.discharge_msg))
                connection.send(discharge)
                sleep(1)
                self.distribute_clients()
                break

            msg = pickle.loads(msg_pickled)
            if user is None and isinstance(msg, Message):
                user = msg.user
                # send entered chat to all clients as soon as user name is known
                self.distribute_message(Message(Message.server_user, "'" + user + "' entered the chat."))
                print("sent entered to all clients")

            self.messages.append(msg)

            self.vprint(msg.user + ": " + msg.message)
            self.distribute_message(msg)
            if not msg_pickled:
                break

        connection.close()

    def distribute_bytes(self, byt):
        """
        sends the given bytes to all clients
        :param byt: bytes like object
        """
        with self.clients_lock:
            for client in self.clients:
                client.send(byt)

    def distribute_clients(self):
        """
        Sends current clients list to all clients
        :return:
        """
        clients_pickled = pickle.dumps(self.clients)
        self.distribute_bytes(Message.client_list_update)
        sleep(0.1)
        self.distribute_bytes(clients_pickled)

    def distribute_message(self, msg):
        """
        Sends the given message to all connected clients
        :param msg: Message object
        """
        if isinstance(msg, Message):
            msg = pickle.dumps(msg)
        else:
            self.vprint("Warning: distribute_message got non Message object, sending like is. ")
        self.distribute_bytes(msg)


