import asyncio
import os
from creart import create
from yarl import URL

from avilla.core.elements import Text
from avilla.core import Avilla, Context, MessageReceived
from avilla.core.elements import Notice, Picture
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.resource import LocalFileResource

from avilla.qqguild.connection.ws_client import QQGuildWsClientConfig, QQGuildWsClientNetworking, Intents
from avilla.qqguild.protocol import QQGuildProtocol

# from graia.amnesia.builtins.aiohttp import AiohttpClientService
from graia.broadcast import Broadcast
from launart import Launart

#from avilla.console.protocol import ConsoleProtocol

import richuru1
#richuru1.install()

broadcast = create(Broadcast)
launart = Launart()
protocol = QQGuildProtocol()
service = protocol.service
config = QQGuildWsClientConfig(
    os.getenv("QQGUILD_ID"),
    os.getenv("QQGUILD_TOKEN"),
    os.getenv("QQGUILD_SECRET"),
    is_sandbox=True,
    intent=Intents(guild_messages=True),
)
conn = QQGuildWsClientNetworking(protocol, config)
service.connections.append(conn)

#console_protocol = ConsoleProtocol()
avilla = Avilla(broadcast, launart, [protocol], message_cache_size=0)

protocol.avilla = avilla



#debug(protocol.isolate.artifacts)
# exit()

# TODO(Networking): 自动注册 Account


@broadcast.receiver(MessageReceived)
async def on_message_received(cx: Context, event: MessageReceived):
    # debug(cx.artifacts.maps)
    print(cx.endpoint, cx.client)
    await cx.scene.send_message(str(event.message.content.include(Text)), reply=event.message)
    print(
        await cx.scene.send_message("Hello! Avilla", reply=event.message)
    )


avilla.launch_manager.launch_blocking(loop=broadcast.loop)
