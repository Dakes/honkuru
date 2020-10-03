import pickle
import socket

from message import Message

class Client(object):

    def __init__(self, sip, sport):
        self.server_ip = sip
        self.server_port = sport


    def client(self):
        client_socket = socket.socket()
        print('Waiting for connection')
        try:
            client_socket.connect((self.server_ip, self.server_port))
        except socket.error as e:
            print(str(e))

        resp = client_socket.recv(1024)
        print(resp.decode('utf-8'))
        while True:
            msg = input('send: ')
            # prevent sending of empty String
            msg = " " if not msg else msg

            client_socket.send(msg.encode('utf-8', 'replace'))
            resp = client_socket.recv(1024)
            print(resp.decode('utf-8'))

            if msg == Message.disconnect:
                break

        client_socket.close()


