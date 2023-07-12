from matrix_client.client import MatrixClient


events = ['on_message', 'on_ready', 'on_cipher']


class Bot:
    def __init__(self, username: str, password: str, prefix=".", log_function=lambda text: print("WARNING:", text)):
        self.events = {}
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

    def listener(self, ctx):
        if ctx['type'] == "m.room.message":
            self.events['on_message'](Context(ctx, self))
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


class Context:
    def __init__(self, ctx: dict, bot: Bot):
        self.type = ctx['type']
        self.author = ctx['sender'] # TODO: use an Author object instead of a string
        self.room = ctx['room_id'] # TODO: use a Room object
        self.bot = bot
        if 'content' in ctx.keys():
            self.msgtype = ctx['content']['msgtype']
            if self.msgtype == "m.text":
                self.content = ctx['content']['body']

    def send(self, text):
        room = self.bot.client.join_room(self.room)
        room.send_text(text)

