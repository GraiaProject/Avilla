import asyncio
import os
from creart import create
from yarl import URL

from avilla.core import Avilla, Context, MessageReceived
from avilla.core.elements import Notice, Picture
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.resource import LocalFileResource

from avilla.qqguild.connection.ws_client import QQGuildWsClientConfig, QQGuildWsClientNetworking
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
    os.getenv("BBOT_ID"),
    os.getenv("BBOT_TOKEN"),
    os.getenv("BBOT_SECRET")
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
    print(cx.endpoint, cx.scene, cx.client, cx.self, cx.account)



avilla.launch_manager.launch_blocking(loop=broadcast.loop)
