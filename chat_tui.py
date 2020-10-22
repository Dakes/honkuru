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


class ChatTUI(object):

    def __init__(self, send=None, messages=None):
        self.send = send

        # Style.
        self.classic_style = Style(
            [
                ("output-field", "bg:#000044 #ffffff"),
                ("input-field", "bg:#000000 #ffffff"),
                ("line", "#004400"),
            ]
        )

        self.style = self.classic_style

        self.welcome_txt = """
        Welcome to honkuru. The peer-to-peer text chat. 
        To send a message just type it and send with 'enter'. 
        To display this help message type '!help'\n
        """
        self.welcome_msg = Message(Message.server_user, self.welcome_txt)


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
            event.app.exit()
            # TODO: make close connection function
            exit(1)

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

    '''
    def receive_msg(self, msg):
        """
        adds a message to the message box
        :param msg: Message object
        :return:
        """
        # print("TUI received: " + msg)
        # Add text to output buffer.
        user_msg = msg.user + ": " + msg.message
        new_text = self.output_field.text + user_msg

        self.output_field.buffer.document = Document(
            text=new_text, cursor_position=len(new_text)
        )

        self.application.invalidate()
    '''

    def send_message(self, buff):
        self.send(self.input_field.text)

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
                user_msg = msg.user + ": " + msg.message
                # new_text = self.output_field.text + user_msg

                self.output_field.buffer.document = Document(
                    text=new_text, cursor_position=len(new_text)
                )
                msg_len = len(self.messages)
                # self.application.invalidate()


if __name__ == "__main__":
    ui = ChatTUI()
    ui.main()

