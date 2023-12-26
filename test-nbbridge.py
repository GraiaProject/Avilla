from avilla.core import Avilla, Context, MessageReceived
from avilla.console.element import Markdown

from avilla.nonebridge.service import NoneBridgeService
from avilla.onebot.v11.protocol import OneBot11Protocol, OneBot11ReverseConfig

from graia.amnesia.builtins.asgi import UvicornASGIService

import nonebot

from avilla.core.elements import Emoji

avilla = Avilla()


config = OneBot11ReverseConfig("/ob", "dfawdfafergergeaar")
avilla.apply_protocols(OneBot11Protocol().configure(config))
avilla.launch_manager.add_component(UvicornASGIService("127.0.0.1", 9090))
avilla.launch_manager.add_component(NoneBridgeService(avilla))
nonebot.load_plugin("nonebot_world")

#@avilla.listen(MessageReceived)
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

avilla.launch()
