import datetime


class Message(object):
    command_prefix = "!"
    help = command_prefix + "help"
    disconnect = command_prefix + "disconnect"
    theme = command_prefix + "theme"

    welcome_message = "Welcome to the chatroom. "
    discharge_msg = "Goodbye! "

    server_user = "Server"
    client_user = "Client"
    anonymous_user = "Anonymous"

    # constant strings for background communication between client and server
    # sent to server ip & port to see if server is running
    check_available = b"aep7OoQu7ie3eeng7jeeCahXoh3iegha"
    # answer if server is running
    server_available = b"au3athei9pifoh4Aexu4raf9keic1ui7"
    # Communicates to server that client wants to connect
    client_connection = b"ie6peeL8asi4Zie8thuChee1ejooxies"
    # signal to close the connection from client to server
    close_connection_client = b"geingohveequ3ooKatooJ8oomiCifihe"
    # signal to close the connection from server to client
    # close_connection_server = b"eiYahg3aephaesh3ceb8rie0piahairo"
    # if this is received by client, the next message will be a new client list.
    client_list_update = b"ahphahKoo9biupheer4HaiCheiwa4hie"
    # sent from server to clients if server is shutting down
    server_shutdown = b"dohk0Yei8ahrahwi5aejoe4utaid7tho"
    # sent from server to client to request username
    send_username = b"hoh6xahchuShinei5bietah7ahvuth2f"

    all_codes = (check_available, server_available, client_connection, close_connection_client, client_list_update,
                 server_shutdown, send_username)

    def __init__(self, usr, msg):
        self.user = usr
        self.send_time = datetime.datetime.now()
        self.message = msg


