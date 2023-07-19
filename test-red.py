import asyncio
import os
from creart import create
from yarl import URL

from avilla.core.elements import Text
from avilla.core import Avilla, Context, MessageReceived
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.resource import LocalFileResource

from avilla.red.net.ws_client import RedWsClientNetworking, RedWsClientConfig
from avilla.red.protocol import RedProtocol

# from graia.amnesia.builtins.aiohttp import AiohttpClientService
from graia.broadcast import Broadcast
from launart import Launart

# from avilla.console.protocol import ConsoleProtocol

import richuru1

# richuru1.install()

broadcast = create(Broadcast)
launart = Launart()
protocol = RedProtocol()
service = protocol.service
config = RedWsClientConfig(
    URL("ws://localhost:16530"),
    os.getenv("QQNT_TOKEN")
)
conn = RedWsClientNetworking(protocol, config)
service.connections.append(conn)

# console_protocol = ConsoleProtocol()
avilla = Avilla(broadcast, launart, [protocol], message_cache_size=0)

protocol.avilla = avilla


# debug(protocol.isolate.artifacts)
# exit()

# TODO(Networking): 自动注册 Account


@broadcast.receiver(MessageReceived)
async def on_message_received(cx: Context, event: MessageReceived):
    # debug(cx.artifacts.maps)
    print(cx.endpoint, cx.client)
    print(event.message.content)
    if cx.scene.follows("::group(481878114)") or cx.scene.follows("::group(941310484)"):
        await cx.scene.send_message("Hello, Avilla!")

    if str(event.message.content).startswith("echo"):
        content = str(event.message.content)[4:].lstrip()
        await cx.scene.send_message(
            [
                Text(content),
            ],
        )


avilla.launch_manager.launch_blocking(loop=broadcast.loop)
