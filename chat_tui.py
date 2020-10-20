import urwid
from message import Message

from prompt_toolkit.application import Application
from prompt_toolkit.document import Document
from prompt_toolkit.filters import has_focus
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import SearchToolbar, TextArea


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

        self.welcome_message = """
        Welcome to honkuru. The peer-to-peer text chat. 
        To send a message just type it and send with 'enter'. 
        To display this help message type '!help'
        """

        # self.palette = self.classic_theme

        # reference to messages object of client
        self.messages = messages

        # self.draw()


    def main(self):
        # The layout.
        self.output_field = TextArea(style="class:output-field", text=self.welcome_message)
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
        application = Application(
            layout=Layout(container, focused_element=self.input_field),
            key_bindings=kb,
            style=self.style,
            mouse_support=True,
            full_screen=True,
        )

        application.run()

    # Attach accept handler to the input field. We do this by assigning the
    # handler to the `TextArea` that we created earlier. it is also possible to
    # pass it to the constructor of `TextArea`.
    # NOTE: It's better to assign an `accept_handler`, rather then adding a
    #       custom ENTER key binding. This will automatically reset the input
    #       field and add the strings to the history.
    def accept(self, buff):
        # Evaluate "calculator" expression.
        try:
            output = "\n\nIn:  {}\nOut: {}".format(
                self.input_field.text, eval(self.input_field.text)
            )  # Don't do 'eval' in real code!
        except BaseException as e:
            output = "\n\n{}".format(e)
        new_text = self.output_field.text + output

        # Add text to output buffer.
        self.output_field.buffer.document = Document(
            text=new_text, cursor_position=len(new_text)
        )

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

    def send_message(self, buff):

        self.send(self.input_field.text)



    def draw(self):
        # while True:
        send_line = urwid.Edit(u"Send: ")
        fill = InputBox(send_line)
        fill.set_vars(send_line, self.send)
        loop = urwid.MainLoop(fill, unhandled_input=self.exit_on_q)
        msg_box = self.draw_messages()
        loop.run()

    def exit_on_q(self, key):
        if key in ('esc',):
            raise urwid.ExitMainLoop()

    def draw_messages(self):
        # print(self.messages)
        msgs = ""
        for msg in self.messages:
            msgs = msgs + msg.user + ": " + msg.message + "\n"
        msg_box = urwid.Text(msgs)
        return msg_box


class InputBox(urwid.Filler):
    # def __init__(self, edit):
        # self.edit_text = edit
    def set_vars(self, edit, send):
        self.edit = edit
        self.send = send

    def keypress(self, size, key):
        if key != 'enter':
            return super(InputBox, self).keypress(size, key)
        # send message
        # self.edit.edit_text
        self.send(self.edit.edit_text)
        self.original_widget = urwid.Text(
            "send: "
        )


if __name__ == "__main__":
    ui = ChatTUI()
    ui.main()

