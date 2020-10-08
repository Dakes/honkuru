import os
from time import sleep
import socket
import configparser
from itertools import chain
import re
from threading import Thread

import client, server
from message import Message

class Honkuru(object):

    def __init__(self):
        # get config path
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(path, 'config.cfg')
        # parse config
        config = configparser.ConfigParser()
        config.read(path)
        # TODO: check port and IP for validity
        self.server_port = int(config["server"]["port"])
        self.server_ip = config["server"]["ip"]
        self.client_ports = self.parse_range_list(config["client"]["ports"])

        # test if a server is available on server_port
        server_exist = self.check_server()
        sleep(0.1)
        self.server = False

        if not server_exist:
            print("Server not detected at: ", self.server_ip+":"+str(self.server_port))
            print("Entering Server mode")
            self.server = True
        else:
            print("Server detected at: ", self.server_ip+":"+str(self.server_port))
            print("Entering Client mode")

    def check_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self.server_ip, self.server_port))
            s.send(Message.check_available)
            result = s.recv(1024)
            print("result: ", result)
            s.close()
            if result == Message.server_available:
                return True
            else:
                return False
        except ConnectionRefusedError:
            return False
        except OverflowError as err:
            print(err)
            exit(1)

    def main(self):
        if self.server:
            s = server.Server(self.server_ip, self.server_port, self.client_ports)
            # s.server()
            server_thread = Thread(target=s.server, args=())
            server_thread.start()

            # c = client.Client(self.server_ip, self.server_port)
            # c.client()
            # client_thread = Thread(target=c.client, args=())
            # client_thread.start()
        else:
            c = client.Client(self.server_ip, self.server_port)
            c.client()
        # TODO: add server only mode

    def parse_range_list(self, rgstr):
        """
        Parses a list of integers in a string, in the form: "7951 - 7999, 8001, 8012" into an integer array
        Copied from https://gist.github.com/kgaughan/2491663
        :param rgstr: String of integers separated by "," of "-"
        :return: int Array
        """
        def parse_range(rg):
            if len(rg) == 0:
                return []
            parts = re.split(r'[:-]', rg)
            if len(parts) > 2:
                raise ValueError("Invalid range: {}".format(rg))
            try:
                return range(int(parts[0]), int(parts[-1]) + 1)
            except ValueError:
                if len(parts) == 1:
                    print("Strings are not allowed. ", "Please remove:", parts)
                    exit(1)
                else:
                    raise ValueError("Non-integer range: {}".format(rg))

        rg = map(parse_range, re.split("\s*[,;]\s*", rgstr))
        return list(set(chain.from_iterable(rg)))


if __name__ == "__main__":
    honkuru = Honkuru()
    honkuru.main()

