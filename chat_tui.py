from time import sleep

from message import Message

from prompt_toolkit.application import Application
from prompt_toolkit.document import Document
from prompt_toolkit.filters import has_focus
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import SearchToolbar, TextArea

import _thread
import threading
import multiprocessing
import colorama


class ChatTUI(object):

    def __init__(self, client=None, messages=None):
        self.client = client
        self.send = self.client.send

        # Style.
        self.classic_style = Style(
            [
                ("output-field", "bg:#000044 #ffffff"),
                ("input-field", "bg:#000000 #ffffff"),
                ("line", "#004400"),
            ]
        )

        self.dark_mode = Style(
            [
                ("output-field", "bg:#2b2b2b #ffffff"),
                ("input-field", "bg:#000000 #ffffff"),
                ("line", "#004400"),
            ]
        )

        self.dakes_theme = Style(
            [
                ("output-field", "bg:#004400 #ffffff"),
                ("input-field", "bg:#000000 #ffffff"),
                ("line", "#aa007f"),
            ]
        )

        self.themes = ["classic style", "dark mode", "dakes theme"]

        self.themes_help_txt = "Available themes  are: \n" + str(self.themes) + \
                               '\nYou select a theme by typing: "!theme classic style"'

        self.themes_help_msg = Message(Message.server_user, self.themes_help_txt)

        self.style = self.classic_style

        self.welcome_txt = """
        Welcome to honkuru. The peer-to-peer text chat. 
        To send a message just type it and send with 'enter'. 
        To display the help message type '!help'\n
        """
        self.welcome_msg = Message(Message.server_user, self.welcome_txt)

        self.help_txt = """To display this help type: {}
        To display all available color themes type: {}
        To disconnect type: {}
        or Press Ctrl+C or Ctrl+Q""".format(Message.help, Message.theme, Message.disconnect)
        self.help_msg = Message(Message.server_user, self.help_txt)




        # reference to messages object of client
        self.manager = multiprocessing.Manager()

        self.messages = messages
        self.messages.append(self.welcome_msg)

        self.application = Application()

        # self.draw()


    def main(self):
        # The layout.
        self.output_field = TextArea(style="class:output-field", text=self.welcome_msg.message)
        self.input_field = TextArea(
            height=1,
            prompt=">>> ",
            style="class:input-field",
            multiline=False,
            wrap_lines=False,
        )

        container = HSplit(
            [
                self.output_field,
                Window(height=1, char="-", style="class:line"),
                self.input_field,
            ]
        )

        self.input_field.accept_handler = self.send_message

        # The key bindings.
        kb = KeyBindings()

        @kb.add("c-c")
        @kb.add("c-q")
        def _(event):
            """ Pressing Ctrl-Q or Ctrl-C will exit the user interface. """
            self.client.client_socket.send(Message.close_connection_client)
            sleep(2)
            event.app.exit()

        # Run application.
        self.application = Application(
            layout=Layout(container, focused_element=self.input_field),
            key_bindings=kb,
            style=self.style,
            mouse_support=True,
            full_screen=True,
        )

        # _thread.start_new_thread(self.render_messages, ("Thread-1", 2,))

        t = threading.Thread(
            target=self.render_messages,
            args=(),
        )
        t.daemon = True
        t.start()

        self.application.run()

    def send_message(self, buff):
        """
        Will send the message typed by calling the reference to the send function of the client
        Also handles some special command, like theme changing
        :param buff:
        :return:
        """
        msg = self.input_field.text

        if msg and msg[0] == Message.command_prefix:
            # change color themes
            if Message.theme in msg:
                theme = msg.lstrip(Message.theme).lstrip()
                if theme == "classic style" or theme == "classic_style":
                    self.style = self.classic_style
                elif theme == "dark mode" or theme == "dark_mode":
                    self.style = self.dark_mode
                elif "dakes" in theme:
                    self.style = self.dakes_theme

                else:
                    self.messages.append(self.themes_help_msg)
                self.application.style = self.style

            # disconnect is handled by client
            elif Message.disconnect in msg:
                # self.disconnect()
                self.client.client_socket.sendall(Message.close_connection_client)
                # self.client.disconnect()
                # self.disconnect()

            # help Message
            elif Message.help in msg:
                self.messages.append(self.help_msg)

        else:
            self.client.send(msg)

    def render_messages(self):
        msg_len = 0
        while True:
            sleep(0.01)
            if msg_len < len(self.messages):

                # print(self.messages)
                new_text = ""
                msg = ""
                for msg in self.messages:
                    new_text = new_text + "\n" + msg.user + ": " + msg.message

                self.output_field.buffer.document = Document(
                    text=new_text, cursor_position=len(new_text)
                )
                msg_len = len(self.messages)

    def disconnect(self):
        self.messages.append(Message(Message.client_user, "Disconnecting... "))
        sleep(2)
        try:
            self.application.exit()
        except Exception:
            pass


if __name__ == "__main__":
    ui = ChatTUI()
    ui.main()

