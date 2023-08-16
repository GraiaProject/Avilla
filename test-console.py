from avilla.core import Avilla, Context, MessageReceived
from avilla.console.protocol import ConsoleProtocol
from avilla.console.element import Markdown, Emoji

from avilla.nonebridge.service import NoneBridgeService
from avilla.onebot.v11.protocol import OneBot11Protocol
from avilla.onebot.v11.net.ws_server import OneBot11WsServerConfig, OneBot11WsServerNetworking

from graia.amnesia.builtins.asgi import UvicornASGIService

import nonebot

avilla = Avilla()
#avilla.apply_protocols(ConsoleProtocol())


protocol = OneBot11Protocol()
service = protocol.service

# config = OneBot11WsClientConfig(URL(A60_ENDPOINT), A60_SECRET)
# conn = OneBot11WsClientNetworking(protocol, config)
# service.connections.append(conn)

config = OneBot11WsServerConfig("/ob", "dfawdfafergergeaar")
net = OneBot11WsServerNetworking(protocol, config)
service.connections.append(net)

avilla.apply_protocols(protocol)

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
