import datetime


class Message(object):
    command_prefix = "!"
    help = command_prefix + "help"
    disconnect = command_prefix + "disconnect"
    theme = command_prefix + "theme"

    welcome_message = "Welcome to the chatroom. "
    discharge_msg = "Goodbye! "

    server_user = "server"
    client_user = "client"
    anonymous_user = "Anonymous"

    # constant strings for background communication between client and server
    # sent to server ip & port to see if server is running
    check_available = b"aep7OoQu7ie3eeng7jeeCahXoh3iegha"
    # answer if server is running
    server_available = b"au3athei9pifoh4Aexu4raf9keic1ui7"
    # Communicates to server that client wants to connect
    client_connection = b"ie6peeL8asi4Zie8thuChee1ejooxies"
    # signal to close the connection
    close_connection = b"geingohveequ3ooKatooJ8oomiCifihe"
    # if this is received by client, the next message will be a new client list.
    client_list_update = b"ahphahKoo9biupheer4HaiCheiwa4hie"

    def __init__(self, usr, msg):
        self.user = usr
        self.send_time = datetime.datetime.now()
        self.message = msg


