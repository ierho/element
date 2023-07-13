# element.py
## Info
This is an SDK for app.element.io based on [matrix_client](https://github.com/matrix-org/matrix-python-sdk/tree/master). It is made for people from `discord.py`. This library does not use async/await.
## Installation
To install use `pip3 install element-sdk`
## Benefits
It is very simple, fast and similar to `discord.py` so people from discord can make element bots easier. File upload, admin commands, etc. are supported.
## Downsides
It does not support encrypted channels, voice messages and voice channels yet.
## Example
This is a basic example of a bot with a demonstration of events and commands. By the way, the name of the library is supposed to be element and not element-sdk:
```py
from element import *

client = Bot(prefix=".")


@client.event
def on_ready():
    print("Ready!")


@client.command
def ping(ctx: Context):
    if ctx.author != "@bot_name:matrix.org":
        ctx.send("Pong")


client.run("bot_name", "password")

```