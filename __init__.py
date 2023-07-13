import matrix_client.client
from matrix_client.client import MatrixClient

events = ['on_message', 'on_ready', 'on_cipher']


class Bot:
    def __init__(self, username: str, password: str, prefix=".", log_function=lambda text: print("WARNING:", text), api="https://matrix-client.matrix.org"):
        self.events = {}
        self.commands = {}
        self.log = log_function
        self.prefix = prefix
        for i in events:
            self.events[i] = lambda ctx=None: None
        self.api = api
        self.client = MatrixClient(self.api)
        self.client.login(username=username, password=password, sync=True)
        self.running = True

    def event(self, func):
        name = func.__name__
        if name in events:
            self.events[name] = func
            return
        else:
            pass  # raise an error

    def command(self, func):
        name = func.__name__
        self.commands[self.prefix + name] = func

    def listener(self, ctx):
        context = Context(ctx, self)
        if ctx['type'] == "m.room.message":
            self.events['on_message']()
            split = context.content.split()
            for key in self.commands.keys():
                if split[0] == key:
                    self.commands[key](context, *split[1:])
                    return
        elif ctx['type'] == "m.room.encrypted":
            self.events['on_cipher'](Context(ctx, self))
        else:
            self.log("Unknown event")

    def run(self, loop=True):
        self.client.add_listener(self.listener)
        self.client.start_listener_thread()
        self.events['on_ready']()
        if loop:
            while self.running:
                pass


class Room:
    def __init__(self, room_id: str, bot: Bot):
        self.room_id = room_id
        self.bot = bot
        self.room = self.bot.client.join_room(self.room_id)

    def send(self, text):
        self.room.send_text(text)

    def __eq__(self, other):
        if type(other) is Room:
            return other.room_id == self.room_id
        return self.room_id == other


class User:
    def __init__(self, username, bot: Bot):
        self.username = username
        self.bot = bot
        self.matrix_user = matrix_client.client.User(self.bot.client.api, self.username)
        self.display_name = self.matrix_user.get_display_name()
        self.avatar_url = self.matrix_user.get_avatar_url()

    def __eq__(self, other):
        if type(other) == User:
            return self.username == other.username
        if self.username == other:
            return True
        return self.display_name == other

    def __str__(self):
        return self.username


class Context:
    def __init__(self, ctx: dict, bot: Bot):
        self.type = ctx['type']
        self.author = User(ctx['sender'], bot)
        self.room = Room(ctx['room_id'], bot)
        self.bot = bot
        if 'content' in ctx.keys():
            self.message_type = ctx['content']['msgtype']
            if self.message_type == "m.text":
                self.content = ctx['content']['body']

    def send(self, text):
        self.room.send(text)
