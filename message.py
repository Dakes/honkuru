import datetime


class Message(object):
    command_prefix = "!"
    help = command_prefix + "help"
    disconnect = command_prefix + "disconnect"
    theme = command_prefix + "theme"

    discharge_msg = "Goodbye! "

    server_user = "server"

    # constant strings for background communication
    check_available = b"aep7OoQu7ie3eeng7jeeCahXoh3iegha"
    server_available = b"au3athei9pifoh4Aexu4raf9keic1ui7"
    client_connection = b"ie6peeL8asi4Zie8thuChee1ejooxies"

    def __init__(self, usr, msg):
        self.user = usr
        self.send_time = datetime.datetime.now()
        self.message = msg


