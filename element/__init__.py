import requests
from .errors import *
from .matrix_client import *
from .matrix_client.client import MatrixClient

events = ['on_message', 'on_ready', 'on_cipher', 'on_message_delete', 'on_invite', 'on_leave', 'on_image']

video = [".mp4", ]
audio = [".mp3", ".wav"]
image = [".png", ".jpg", ".jpeg"]


def find_content_type(filename: str):
    for i in video:
        if filename.startswith(i):
            return "video"
    for i in audio:
        if filename.startswith(i):
            return "audio"
    for i in image:
        if filename.startswith(i):
            return "image"
    return "file"


class Bot:
    def __init__(self, prefix=".",
                 log_function=lambda text: print("WARNING:", text),
                 api="https://matrix-client.matrix.org"):
        self.events = {}
        self.commands = {}
        self.log = log_function
        self.prefix = prefix
        for i in events:
            self.events[i] = lambda ctx=None: None
        self.api = api
        self.client = MatrixClient(self.api)
        self.running = True

    def event(self, func):
        name = func.__name__
        if name in events:
            self.events[name] = func
            return
        else:
            raise UnknownEvent(f"Event '{name}' does not exist.")

    def command(self, func):
        name = func.__name__
        self.commands[self.prefix + name] = func

    def listener(self, ctx):
        context = Context(ctx, self)
        if ctx['type'] == "m.room.message":
            if context.file is None:
                self.events['on_message'](context)
                split = context.content.split()
                for key in self.commands.keys():
                    if split[0] == key:
                        self.commands[key](context, *split[1:])
                        return
            else:
                self.events['on_image'](context)
        elif ctx['type'] == "m.room.encrypted":
            self.events['on_cipher'](context)
        elif ctx['type'] == "m.room.message":
            self.events['on_message_delete'](context)
        elif ctx['type'] == "m.room.member":
            if ctx['content']['membership'] == "invite":
                self.events['on_invite'](context)
            elif ctx['content']['membership'] == "leave":
                self.events['on_leave'](context)
        else:
            self.log("Unknown event")

    def run(self, username, password, loop=True):
        self.client.login(username=username, password=password, sync=True)
        self.client.add_listener(self.listener)
        self.client.start_listener_thread()
        self.events['on_ready']()
        if loop:
            while self.running:
                pass

    def close(self):
        self.running = False


class File:
    def __init__(self, content=None, content_type: str = None, filename: str = None, url: str = None, bot: Bot = None):
        self.url = url
        self.bot = bot
        self.content = content
        if content_type is None:
            if filename is not None:
                self.content_type = find_content_type(filename)
        else:
            self.content_type = content_type
        self.filename = filename

    def download_url(self, bot: Bot = None):
        if bot is None:
            matrix_bot = self.bot
        else:
            matrix_bot = bot
        if type(self.url) is str:
            return matrix_bot.client.api.get_download_url(self.url)
        return None

    def download(self, path, bot: Bot = None):
        if bot is None:
            matrix_bot = self.bot
        else:
            matrix_bot = bot
        if type(self.url) is str:
            return matrix_bot.client.api.get_download_url(self.url)
        content = requests.get(matrix_bot.client.api.get_download_url(self.url)).content
        with open(path, "wb") as f:
            f.write(content)

    def upload(self, bot: Bot = None):
        if bot is None:
            matrix_bot = self.bot
        else:
            matrix_bot = bot
        if type(self.url) is str:
            return matrix_bot.client.api.get_download_url(self.url)
        self.url = matrix_bot.client.upload(
            content=self.content,
            content_type=self.content_type,
            filename=self.filename
        )
        return self.url


class Room:
    def __init__(self, room_id: str, bot: Bot):
        self.room_id = room_id
        self.bot = bot
        self.room: matrix_client.client.Room = self.bot.client.join_room(self.room_id)

    def send(self, text=None, file: File = None):
        ctx_image = None
        if file is not None:
            file.upload()
            if file.content_type == "file":
                ctx_image = self.room.send_file(file.url, file.filename)
            elif file.content_type == "video":
                ctx_image = self.room.send_video(file.url, file.filename)
            elif file.content_type == "image":
                ctx_image = self.room.send_image(file.url, file.filename)
            elif file.content_type == "audio":
                ctx_image = self.room.send_audio(file.url, file.filename)
        if text is not None:
            return self.room.send_text(text)
        if ctx_image is None:
            raise EmptyMessage("text is None and file is None")
        return Context(ctx_image, self.bot)

    def kick(self, user_id, reason=""):
        return self.room.kick_user(user_id=user_id, reason=reason)

    def ban(self, user_id, reason=""):
        return self.room.ban_user(user_id=user_id, reason=reason)

    def invite(self, user_id):
        return self.room.invite_user(user_id=user_id)

    def leave(self):
        return self.room.leave()

    def delete(self, event_id, reason=None):
        return self.room.redact_message(event_id=event_id, reason=reason)

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
        self.ctx = ctx
        self.content = ""
        self.file = None
        if 'type' in ctx.keys():
            self.type = ctx['type']
        self.event_id = ctx['event_id']
        if 'sender' in ctx.keys():
            self.author = User(ctx['sender'], bot)
        if 'room_id' in ctx.keys():
            self.room = Room(ctx['room_id'], bot)
        self.bot = bot
        if 'content' in ctx.keys():
            if 'msgtype' in ctx['content'].keys():
                self.message_type = ctx['content']['msgtype']
                if self.message_type == "m.text":
                    self.content = ctx['content']['body']
                elif self.message_type == "m.image":
                    self.file = File(url=ctx['content']['url'], bot=bot)
            if 'displayname' in ctx['content'].keys():
                self.displayname = ctx['content']['displayname']
            if 'membership' in ctx['content'].keys():
                self.membership = ctx['content']['membership']

    def delete(self, reason=None):
        return Context(self.room.delete(self.event_id, reason=reason), bot=self.bot)

    def send(self, text, file: File = None):
        return Context(self.room.send(text, file=file), bot=self.bot)

    def reply(self, text):
        f_body = "<mx-reply><blockquote>"
        f_body += f"<a href='https://matrix.to/#/{self.room.room_id}/{self.event_id}?via=matrix.org\">In reply to</a>"
        f_body += f" <a href=\"https://matrix.to/#/{self.author.username}\">{self.author.username}</a>"
        f_body += f"<br>{self.content}</blockquote></mx-reply>."

        content = {
            "msgtype": "m.room.message",
            "body": text,
            "format": "org.matrix.custom.html",
            "formatted_body": f_body,
            "m.relates_to": {"m.in_reply_to": {"event_id": self.event_id}}
        }
        return Context(self.bot.client.api.send_message_event(
            self.room.room_id, "m.room.message",
            content,
            None
            ),
            bot=self.bot
        )
