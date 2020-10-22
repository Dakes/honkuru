import pickle
import socket
import multiprocessing
import threading
from time import sleep

from message import Message

from chat_tui import ChatTUI


# tmp
from playsound import playsound

class Client(object):

    def __init__(self, sip, sport):
        self.server_ip = sip
        self.server_port = sport

        self.user = "Anonymous"

        # Array of all past message history. Elements are Message objects
        self.manager = multiprocessing.Manager()
        self.messages = []# self.manager.list([])
        self.client_socket = None

    def client(self):
        ui = ChatTUI(self.send, self.messages)


        self.client_socket = socket.socket()
        # self.client_socket = client_socket
        print('Waiting for connection')
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
        except socket.error as e:
            print(str(e))
            exit(1)

        self.client_socket.send(Message.client_connection)
        self.set_username()

        t = threading.Thread(
            target=ui.main,
            args=(),
        )
        t.daemon = True
        t.start()

        # Receive and print welcome message
        resp_pickled = self.client_socket.recv(4096)
        resp = pickle.loads(resp_pickled)

        self.messages.append(resp)

        while True:
            sleep(1)
            resp_pickled = self.client_socket.recv(4096)
            resp = pickle.loads(resp_pickled)

            self.messages.append(resp)

        client_socket.close()

    def set_username(self):
        usr = input("Please choose a username: ")
        self.user = usr

    def send(self, msg):
        new_msg = Message(self.user, msg)
        msg_pickled = pickle.dumps(new_msg)
        self.client_socket.send(msg_pickled)


    def new_msg(self):
        pass