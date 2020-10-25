import pickle
import socket
import multiprocessing
import threading
from time import sleep

from message import Message

from chat_tui import ChatTUI


class Client(object):

    def __init__(self, sip, sport, verbose=False):
        self.server_ip = sip
        self.server_port = sport

        self.user = "Anonymous"

        # Array of all past message history. Elements are Message objects
        self.manager = multiprocessing.Manager()
        self.messages = []# self.manager.list([])
        self.client_socket = None

        self.verbose = verbose

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

        while True:
            resp = self.recv()
            # print(resp)
            # if isinstance(resp, Message):
            #     print(resp.message)

            # command cases
            # If None is returned the connection is usually down
            if resp is None:
                print("Received 'None' from Server")
                break
            elif resp == Message.close_connection:
                self.disconnect()
                break
            elif isinstance(resp, Message) and resp.message == Message.disconnect:
                self.disconnect()
                break

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


    def recv(self):
        """
        Receive and unpickle a message
        :return: A Message Object
        """
        resp_pickled = self.client_socket.recv(4096)
        if not resp_pickled:
            return None
        resp = pickle.loads(resp_pickled)
        if isinstance(resp, Message):
            self.messages.append(resp)
        return resp

