from matrix_client.client import MatrixClient


events = ['on_message', 'on_ready']


class Bot:
    def __init__(self, username: str, password: str):
        self.events = {}
        self.client = MatrixClient("https://matrix-client.matrix.org")
        self.client.login_with_password(username=username, password=password)

    def event(self, func):
        name = func.__name__
        if name in events:
            self.events[name] = func
            return
        else:
            pass  # raise an error

    def listener(self, ctx):
        for event in self.events.values():
            event(ctx)

    def run(self, loop=True):
        self.client.add_listener(self.listener)
        self.client.start_listener_thread()
        if 'on_ready' in self.events.keys():
            self.events['on_ready']()
        if loop:
            while self.running:
                pass
