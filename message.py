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

    # constant strings for background communication between client and server
    check_available = b"aep7OoQu7ie3eeng7jeeCahXoh3iegha"
    server_available = b"au3athei9pifoh4Aexu4raf9keic1ui7"
    client_connection = b"ie6peeL8asi4Zie8thuChee1ejooxies"
    close_connection = b"geingohveequ3ooKatooJ8oomiCifihe"

    def __init__(self, usr, msg):
        self.user = usr
        self.send_time = datetime.datetime.now()
        self.message = msg


