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
        # List client_information, gets synchronized to all clients. Determines what client will become the next server.
        # Saves the IPs of connected clients with their usernames as keys. Also used by clients to avoid duped usernames
        self.client_information = {}
        self.clients = []
        self.clients_lock = threading.Lock()

        self.last_message = None
        self.messages = []

        self.verbose = verbose
        # verbose print function
        self.vprint = print if self.verbose else lambda *a, **k: None

    def main(self):
        try:
            self.server()
        except KeyboardInterrupt:
            # TODO: not working properly due to Thread
            self.vprint("Caught KeyboardInterrupt")
            self.shutdown()

    def server(self):
        self.server_socket = socket.socket()

        tries = 0
        sleep_duration = 1
        max_seconds = 120
        max_tries = max_seconds / sleep_duration

        while tries < max_tries:
            try:
                self.server_socket.bind((self.server_ip, self.server_port))
                self.vprint("Opened new server. ")
                break
            except socket.error as e:
                # self.vprint(str(e))
                tries += 1
                sleep(sleep_duration)
                if tries % 10 == 0:
                    self.vprint("Still trying to open server. ")
                if tries > max_tries:
                    print("Server could not be opened at: ", self.server_ip, self.server_port)
                    print(e)
                    exit(1)

        self.server_socket.listen(5)

        while True:
            client, address = self.server_socket.accept()
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
                    # _thread.start_new_thread(self.threaded_server, (client,))
                    server_thread = threading.Thread(
                        target=self.threaded_server,
                        args=(client,),
                    )
                    server_thread.daemon = True
                    server_thread.start()
        self.server_socket.close()

    def threaded_server(self, connection):
        # get user name
        user = None
        while not user:
            try:
                connection.send(Message.send_username)
                user = connection.recv(4096).decode()
                self.vprint("Received user name:", user)
                self.add_client_info(user, connection)
                # send entered chat to all clients as soon as user name is known
                self.distribute_message(Message(Message.server_user, "'" + user + "' entered the chat."))
                self.distribute_clients()
            except UnicodeDecodeError as e:
                self.vprint(e)

        wlc = Message(Message.server_user, Message.welcome_message)
        wlc_pickled = pickle.dumps(wlc)
        connection.send(wlc_pickled)

        recv_empty_counter = 0

        while True:
            try:
                msg_pickled = connection.recv(4096)
            except BrokenPipeError:
                self.vprint("client pipe broken, closing connection")
                if user:
                    self.remove_client(connection, user)
                    self.remove_client_info(user)
                else:
                    break

            # skip if string is empty (does not come from client)
            if not msg_pickled:
                recv_empty_counter = recv_empty_counter + 1
                sleep(0.01)
                # close connection if connection is down
                if recv_empty_counter > 1000000:
                    self.vprint("Received too much empty responses. exiting")
                    break
                else:
                    continue
            else:
                recv_empty_counter = 0

            # first check for special codes (sent as string instead of Message object)
            # disconnect
            if msg_pickled == Message.close_connection:

                self.remove_client(connection, user)

                # send discharge message to client and close connection
                discharge = pickle.dumps(Message(Message.server_user, Message.discharge_msg))
                connection.send(discharge)
                connection.send(Message.close_connection)
                sleep(1)
                self.remove_client_info(user)
                self.distribute_clients()
                # If this is the clients server it should shut down
                if self.client:
                    if self.client.user == user:
                        self.shutdown()
                break

            msg = pickle.loads(msg_pickled)

            self.messages.append(msg)

            self.vprint(msg.user + ": " + msg.message)
            self.distribute_message(msg)

        connection.close()

    def remove_client(self, cl, user):
        """
        removes the client and sends disconnected message to all users.
        Assumes, client is not reachable any more due to broken pipe. Only messages all other clients.
        :param cl: client socket connection
        :param user: String, client user name
        :return:
        """
        if user is None:
            user = Message.anonymous_user
        with self.clients_lock:
            self.clients.remove(cl)
        client_disconnected_msg = Message(Message.server_user, "'" + user + "' left the chat.")
        self.distribute_message(client_disconnected_msg)

    def add_client_info(self, user, client):
        ip = client.getpeername()[0]
        self.client_information[user] = ip
        self.vprint("Adding", user, "to client_information with", ip)

    def remove_client_info(self, user):
        self.client_information.pop(user)
        self.vprint("Removing user", user, "from client_information")

    def distribute_bytes(self, byt):
        """
        sends the given bytes to all clients
        :param byt: bytes like object
        """
        with self.clients_lock:
            for cl in self.clients:
                try:
                    cl.send(byt)
                except BrokenPipeError:
                    # in case of broken pipe remove client
                    self.clients.remove(cl)

    def distribute_clients(self):
        """
        Sends current clients list to all clients
        :return:
        """
        clients_pickled = pickle.dumps(self.client_information)
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

    def shutdown(self):
        """
        Communicates to clients that server is shutting down and a new server is needed.
        :return:
        """
        self.vprint("Shutting down Server")
        self.distribute_bytes(Message.server_shutdown)
        sleep(1)
        self.server_socket.close()
        exit(0)


