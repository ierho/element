from matrix_client.client import MatrixClient

events = ['on_message', 'on_ready', 'on_cipher']


class Bot:
    def __init__(self, username: str, password: str, prefix=".", log_function=lambda text: print("WARNING:", text)):
        self.events = {}
        self.commands = {}
        self.log = log_function
        self.prefix = prefix
        for i in events:
            self.events[i] = lambda ctx=None: None
        self.client = MatrixClient("https://matrix-client.matrix.org")
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
        self.commands[self.prefix+name] = func

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


class Context:
    def __init__(self, ctx: dict, bot: Bot):
        self.type = ctx['type']
        self.author = ctx['sender']  # TODO: use a User object instead of a string
        self.room = Room(ctx['room_id'], bot)
        self.bot = bot
        if 'content' in ctx.keys():
            self.message_type = ctx['content']['msgtype']
            if self.message_type == "m.text":
                self.content = ctx['content']['body']

    def send(self, text):
        self.room.send(text)
