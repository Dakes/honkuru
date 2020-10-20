import pickle
import socket

from message import Message

from chat_tui import ChatTUI


class Client(object):

    def __init__(self, sip, sport):
        self.server_ip = sip
        self.server_port = sport

        self.user = "Anonymous"

        # Array of all past message history. Elements are Message objects
        self.messages = []
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


        ui.main()

        # Receive and print welcome message
        resp_pickled = self.client_socket.recv(4096)
        resp = pickle.loads(resp_pickled)
        print(resp.user+":", resp.message)
        ui.receive_msg(resp)

        while True:
            # msg_str = input('send: ')
            # msg = Message(self.user, msg_str)
            # prevent sending of empty String
            # msg = Message(self.user, "") if not msg else msg

            # msg_pickled = pickle.dumps(msg)
            # client_socket.send(msg_pickled)
            resp_pickled = self.client_socket.recv(4096)
            resp = pickle.loads(resp_pickled)
            # print(resp.user+":", resp.message)
            self.messages.append(resp)
            ui.receive_msg(resp)
            # print("")

            # if msg.message == Message.disconnect:
                # break

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