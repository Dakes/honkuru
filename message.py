import datetime

class Message(object):
    command_prefix = "!"
    disconnect = command_prefix + "disconnect"

    def __init__(self, usr, msg):
        self.user = usr
        self.send_time = datetime.datetime.now()
        self.message = msg




