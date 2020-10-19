import urwid
from message import Message


class ChatTUI(object):

    def __init__(self, send, messages):
        self.send = send
        self.classic_theme = [
            ('banner', 'black', 'light gray'),
            ('streak', 'black', 'dark red'),
            ('bg', 'black', 'dark blue'),
        ]

        self.palette = self.classic_theme

        # reference to messages object of client
        self.messages = messages

        # self.draw()

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

    def send_message(self, key):
        if key == "enter":
            pass
            # self.send()
    def draw_messages(self):
        # print(self.messages)
        msgs = ""
        for msg in self.messages:
            msgs = msgs + msg.user + ": " + msg.message + "\n"
        msg_box = urwid.Text(msgs)
        return msg_box

    def receive_msg(self, msg):
        """
        adds a message to the message box
        :param msg: Message object
        :return:
        """
        print("received" + msg)

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

