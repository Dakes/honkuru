import pickle
import socket
import multiprocessing
import threading
from time import sleep

from message import Message

import server
from chat_tui import ChatTUI


class Client(object):

    def __init__(self, sip, sport, serv=None, verbose=False):
        self.server_ip = sip
        self.server_port = sport
        self.server = serv

        self.user = Message.anonymous_user

        self.running = True

        # Array of all past message history. Elements are Message objects
        self.manager = multiprocessing.Manager()
        self.messages = []
        self.client_socket = None

        self.ui = ChatTUI(self, self.messages)

        # List of all other clients, used to determine next server.
        self.clients = {}

        self.verbose = verbose
        # verbose print function
        self.vprint = print if self.verbose else lambda *a, **k: None

    def main(self):
        self.connect_server()
        self.set_username()

        ui_thread = threading.Thread(
            target=self.ui.main,
            args=(),
        )
        ui_thread.daemon = True
        ui_thread.start()

        while self.running:
            self.recv()

        self.ui.disconnect()

    def set_username(self):
        # TODO: check for duplicate usernames. For that receive client dict beforehand.
        usr = ""
        while not usr:
            usr = input("Please choose a username: ")
            if not usr:
                print("Username cannot be empty")
        self.user = usr

    def send(self, msg_txt):
        """
        Creates a Message object, pickles it and sends it to the Server
        :param msg_txt: String: Message to send
        """
        # self.vprint("Sending: "+msg_txt)
        new_msg = Message(self.user, msg_txt)
        msg_pickled = pickle.dumps(new_msg)
        try:
            self.client_socket.sendall(msg_pickled)
        except BrokenPipeError:
            if self.running:
                if not self.connect_server():
                    self.new_server()
            else:
                self.hard_shutdown()

    def disconnect(self):
        """
        Send coded closing message to communicate to server to close the connection.
        Also receives the discharge message
        """
        self.client_socket.sendall(Message.close_connection)
        resp = self.recv()
        self.running = False
        sleep(1)
        self.client_socket.close()
        # execute close function of server if client has a server
        if self.server is not None:
            self.server.shutdown()

    def check_codes(self, msg):
        """
        Check byte String codes, being sent instead of Message object
        :param msg: Message Object or Bytestring
        :return: msg if no code received, None otherwise
        """
        if msg == Message.client_list_update:
            self.recv_client_dict()

        # TODO: remove, should never receive close_connection
        elif msg == Message.close_connection:
            self.disconnect()
            self.running = False

        elif msg == Message.server_shutdown:
            if self.running:
                self.new_server()
        # elif isinstance(msg, Message):
            # if msg.message == Message.disconnect:
                # self.disconnect()
                # self.running = False
        # elif msg is None:
            # self.vprint("Received 'None' or empty response from Server", msg, ". Searching for new Server. ")
            # self.running = False
            # if self.running:
                # pass
                # self.new_server()
            # return None
        elif not msg:
            self.vprint("check_codes: in elif not msg: ", msg)
            # self.running = False
            self.new_server()
        elif msg == Message.send_username:
            self.client_socket.sendall(self.user.encode())
        elif isinstance(msg, bytes) and not isinstance(pickle.loads(msg), Message):
            self.vprint("Received unidentifiable code in check_codes: ", msg)
            try:
                # TODO: sometimes the client dict ends up here, too lazy too fix now. So quick and dirty.
                pot_dict = pickle.loads(msg)
                if isinstance(pot_dict, dict):
                    self.clients = pot_dict

                self.vprint(msg.decode("utf-8"))
            except Exception as e:
                self.vprint(e)
        else:
            return msg

        return None

    def recv_client_dict(self):
        """
        Receives a new list of clients from the server and updates the local list.
        """
        list_pickled = self.client_socket.recv(4096)
        try:
            client_list = pickle.loads(list_pickled)
        except pickle.UnpicklingError as e:
            self.vprint(e)
            return None
        if isinstance(client_list, dict):
            self.clients = client_list
        else:
            self.vprint("recv_client_dict: Received something else than dict: ", type(client_list))

    def recv(self):
        """
        Receive and unpickle a message
        :return: A Message Object
        """
        # TODO: catch ConnectionResetError
        try:
            resp_pickled = self.client_socket.recv(4096)
        except (ConnectionResetError, ConnectionError) as e:
            self.vprint(str(e))
            print("Connection error. exiting. ")
            self.hard_shutdown()

        code = self.check_codes(resp_pickled)
        if not code:
            return None
        resp = pickle.loads(resp_pickled)
        if isinstance(resp, Message):
            self.messages.append(resp)
        return resp

    def new_server(self):
        """
        Will create a new server, or search for a new server,
        depending on, if this server is the next one in the clients list
        """
        # first check if dict is empty.
        if not self.clients:
            print("Clients list is empty. exiting. ")
            self.hard_shutdown()

        new_user = next(iter(self.clients))
        # main will create the new Server
        if new_user == self.user:
            ip = self.clients.pop(self.user)
            self.server_ip = ip
            self.server = server.Server(ip, self.server_port, None, self.verbose)
            server_thread = threading.Thread(target=self.server.main, args=())
            server_thread.start()
        else:
            ip = self.clients.pop(new_user)
            self.server_ip = ip

        connected = self.connect_server()
        # try next one in dict
        if not connected:
            self.new_server()

    def connect_server(self):
        """
        Connects to the server for the current IP and port
        :return: new connection, if success, None otherwise
        """
        if self.client_socket is None:
            print('Waiting for connection')
        else:
            self.vprint('Waiting for new connection')

        self.client_socket = socket.socket()

        tries = 0
        sleep_duration = 1
        max_seconds = 120
        max_tries = max_seconds/sleep_duration

        while tries < max_tries:
            try:
                self.client_socket.connect((self.server_ip, self.server_port))
                self.vprint("Connected to Server")
                break
            except socket.error as e:
                tries += 1
                sleep(sleep_duration)
                # self.vprint(str(e))
                if tries > max_tries:
                    print("Server could not be found at", self.server_ip, self.server_port)
                    print(e)
                    return None

        self.client_socket.sendall(Message.client_connection)
        return self.client_socket

    def hard_shutdown(self):
        self.ui.disconnect()
        if self.server:
            self.server.shutdown()
        sleep(3)
        exit(1)

