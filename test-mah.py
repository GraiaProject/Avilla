import asyncio
import os
from creart import create
from yarl import URL

from avilla.core.elements import Text
from avilla.core import Avilla, Context, MessageReceived
from avilla.core.elements import Notice, Picture
from avilla.standard.qq.elements import Face
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.resource import LocalFileResource
from avilla.core import Selector
from avilla.standard.core.message import MessageRevoke
from avilla.standard.qq.announcement import Announcement

from avilla.elizabeth.connection.ws_client import ElizabethWsClientConfig, ElizabethWsClientNetworking
from avilla.elizabeth.protocol import ElizabethProtocol

# from graia.amnesia.builtins.aiohttp import AiohttpClientService
from graia.broadcast import Broadcast
from launart import Launart


import richuru1
#richuru1.install()

broadcast = create(Broadcast)
launart = Launart()
protocol = ElizabethProtocol()
service = protocol.service
config = ElizabethWsClientConfig(
    URL("http://localhost:9080"),
    "INITKEYWylsVdbr",
    3542928737
)
conn = ElizabethWsClientNetworking(protocol, config)
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
    print(event.message.content)
    if cx.client.follows("::group.member(3165388245)"):
        print(
            await cx.scene.send_message(
                [
                    Notice(cx.client),
                    Text("\nHello, Avilla!"),
                    Picture("C:\\Users\\TR\\Pictures\\QQ图片20210814001401.jpg")
                    # Embed(
                    #     "Test Embed",
                    #     "Hello, Avilla!",
                    #     fields=["line1", "line2"],
                    # )
                ],
            )
        )
        # await asyncio.sleep(1)
        # msg = await cx.scene.send_message("test")
        # await asyncio.sleep(3)
        # await cx[MessageRevoke.revoke](msg)
        print(await cx.account.connection.call("fetch", "friendList", {}))
        async for i in cx.query("land.group(592387986).announcement"):
            print(await cx.pull(Announcement, i))

avilla.launch_manager.launch_blocking(loop=broadcast.loop)
