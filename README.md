# element.py
## Info
This is an SDK for app.element.io based on [matrix_client](https://github.com/matrix-org/matrix-python-sdk/tree/master). It is made for people from `discord.py`. This library does not use async/await.
## Benefits
It is very simple, fast and similair to `discord.py` so people from discord can make element bots easier.
## Downsides
It does not support encrypted channels, voice messages and voice channels.
## Example
This is a basic example of a bot with a demonstration of events and commands:
```py
from element import *

client = Bot("bot_name", "password", prefix=".")


@client.event
def on_ready():
    print("Ready!")


@client.command
def ping(ctx: Context):
    if ctx.author != "@bot_name:matrix.org":
        ctx.send("Pong")


client.run()

```