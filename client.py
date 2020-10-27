import pickle
import socket
import multiprocessing
import threading
from time import sleep

from message import Message

from chat_tui import ChatTUI


class Client(object):

    def __init__(self, sip, sport, server=None, verbose=False):
        self.server_ip = sip
        self.server_port = sport
        self.server = server

        self.user = "Anonymous"

        self.running = True

        # Array of all past message history. Elements are Message objects
        self.manager = multiprocessing.Manager()
        self.messages = []
        self.client_socket = None

        # List of all other clients, used to determine next server.
        self.clients = {}

        self.verbose = verbose
        # verbose print function
        self.vprint = print if self.verbose else lambda *a, **k: None

    def client(self):
        ui = ChatTUI(self, self.messages)

        self.client_socket = socket.socket()
        print('Waiting for connection')
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
        except socket.error as e:
            print(str(e))
            exit(1)

        self.client_socket.send(Message.client_connection)
        self.set_username()

        ui_thread = threading.Thread(
            target=ui.main,
            args=(),
        )
        ui_thread.daemon = True
        ui_thread.start()

        while self.running:
            resp = self.recv()

        ui.disconnect()

    def set_username(self):
        # TODO: check for duplicate usernames
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
        self.vprint("Sending: "+msg_txt)
        new_msg = Message(self.user, msg_txt)
        msg_pickled = pickle.dumps(new_msg)
        self.client_socket.send(msg_pickled)

    def disconnect(self):
        """
        Send coded closing message to communicate to server to close the connection.
        Also receives the discharge message
        """
        self.client_socket.send(Message.close_connection)
        resp = self.recv()
        sleep(1)
        self.client_socket.close()

    def check_codes(self, msg):
        if msg == Message.client_list_update:
            self.recv_client_dict()
            return None
        elif msg == Message.close_connection:
            self.disconnect()
            self.running = False
            return None
        # elif isinstance(msg, Message):
            # if msg.message == Message.disconnect:
                # self.disconnect()
                # self.running = False
        elif msg is None:
            self.vprint("Received 'None' from Server")
            self.running = False
            return None
        elif not msg:
            self.running = False
            return None
        else:
            return msg

    def recv_client_dict(self):
        list_pickled = self.client_socket.recv(4096)
        client_list = pickle.loads(list_pickled)
        self.clients = client_list

    def recv(self):
        """
        Receive and unpickle a message
        :return: A Message Object
        """
        resp_pickled = self.client_socket.recv(4096)
        code = self.check_codes(resp_pickled)
        if not code:
            return None
        resp = pickle.loads(resp_pickled)
        if isinstance(resp, Message):
            self.messages.append(resp)
        return resp

