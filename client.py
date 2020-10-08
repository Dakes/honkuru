import pickle
import socket

from message import Message


class Client(object):

    def __init__(self, sip, sport):
        self.server_ip = sip
        self.server_port = sport

        self.user = "Anonymous"

        self.messages = []

    def client(self):
        client_socket = socket.socket()
        print('Waiting for connection')
        try:
            client_socket.connect((self.server_ip, self.server_port))
        except socket.error as e:
            print(str(e))
            exit(1)

        client_socket.send(Message.client_connection)
        self.set_username()

        # Receive and print welcome message
        resp_pickled = client_socket.recv(4096)
        resp = pickle.loads(resp_pickled)
        print(resp.user+":", resp.message)

        while True:
            msg_str = input('send: ')
            msg = Message(self.user, msg_str)
            # prevent sending of empty String
            # msg = Message(self.user, "") if not msg else msg

            msg_pickled = pickle.dumps(msg)
            client_socket.send(msg_pickled)
            resp_pickled = client_socket.recv(4096)
            resp = pickle.loads(resp_pickled)
            print(resp.user+":", resp.message)
            print("")

            if msg.message == Message.disconnect:
                break

        client_socket.close()

    def set_username(self):
        usr = input("Please choose a username: ")
        self.user = usr

