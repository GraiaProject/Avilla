from creart import create
from launart import Launart
from graia.broadcast import Broadcast

from avilla.core import Avilla, Context, MessageReceived
from avilla.console.protocol import ConsoleProtocol
from avilla.console.element import Markdown, Emoji

broadcast = create(Broadcast)
launart = Launart()
avilla = Avilla(broadcast, launart, [ConsoleProtocol()], message_cache_size=0)


@broadcast.receiver(MessageReceived)
async def on_message_received(ctx: Context, event: MessageReceived):
    msg = str(event.message.content)
    if msg == "/help":
        await ctx.scene.send_message(
            [Markdown("""\
## 菜单
- /help
- /echo
- /md
- /emoji
"""
            )])
    elif msg.startswith("/echo"):
        await ctx.scene.send_message(event.message.content.removeprefix("/echo "))
    elif msg == "/md":
        await ctx.scene.send_message(
            [Markdown("""\
# Avilla-Console

`avilla` 的 `Console` 适配，使用 `Textual`

参考: [`nonebot-adapter-console`](https://github.com/nonebot/adapter-console)

## 样例

```python
from creart import create
from launart import Launart
from graia.broadcast import Broadcast

from avilla.core import Avilla, Context, MessageReceived
from avilla.console.protocol import ConsoleProtocol

broadcast = create(Broadcast)
launart = Launart()
avilla = Avilla(broadcast, launart, [ConsoleProtocol()])


@broadcast.receiver(MessageReceived)
async def on_message_received(ctx: Context):
    await ctx.scene.send_message("Hello, Avilla!")


launart.launch_blocking(loop=broadcast.loop)

```
"""
            )]
        )
    elif msg == "/emoji":
        await ctx.scene.send_message([Emoji("art"), " | this is apple -> ", Emoji("apple")])
    else:
        await ctx.scene.send_message("Hello, Avilla!")

launart.launch_blocking(loop=broadcast.loop)
