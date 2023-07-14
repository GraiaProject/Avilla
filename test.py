import asyncio

from creart import create
from yarl import URL

from avilla.core import Avilla, Context, MessageReceived
from avilla.core.elements import Notice, Picture
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.resource import LocalFileResource
from avilla.onebot.v11.net.ws_client import OneBot11WsClientConfig, OneBot11WsClientNetworking
from avilla.onebot.v11.protocol import OneBot11Protocol

# from graia.amnesia.builtins.aiohttp import AiohttpClientService
from graia.broadcast import Broadcast
from launart import Launart
from test_env import A60_ENDPOINT, A60_SECRET


from avilla.elizabeth.protocol import ElizabethProtocol
from avilla.elizabeth.connection.ws_client import ElizabethWsClientConfig, ElizabethWsClientNetworking


#from avilla.console.protocol import ConsoleProtocol

import richuru1
#richuru1.install()

broadcast = create(Broadcast)
launart = Launart()
protocol = OneBot11Protocol()
service = protocol.service
config = OneBot11WsClientConfig(URL(A60_ENDPOINT), A60_SECRET)
conn = OneBot11WsClientNetworking(protocol, config)
service.connections.append(conn)

platform = Platform(Land("qq"), Abstract("onebot/v11"))


mah = ElizabethProtocol()
conn1 = ElizabethWsClientNetworking(mah, ElizabethWsClientConfig(
    URL("http://localhost:8660/"),
    "tdtogkf123", 2119799445
))
mah.service.connections.append(conn1)

#console_protocol = ConsoleProtocol()
avilla = Avilla(broadcast, launart, [protocol, mah], message_cache_size=0)

protocol.avilla = avilla



#debug(protocol.isolate.artifacts)
# exit()

# TODO(Networking): 自动注册 Account


@broadcast.receiver(MessageReceived)
async def on_message_received(cx: Context, event: MessageReceived):
    # debug(cx.artifacts.maps)
    print(cx.endpoint, cx.scene, cx.client, cx.self, cx.account)
    if cx.client.follows("::group.member(1846913566)"):
        #await cx.scene.send_message(
        #    [
        #        "Hello, Avilla!",
        #        Notice(cx.scene.member("1846913566")),
        #        Picture(LocalFileResource("D:/kaf.webp")),
        #    ]
        #)
        print(await conn1.call("get", "friendList"))
    elif cx.client.follows("::land(console).console(console_user)"):
        await cx.scene.send_message("Hello, Console User!")


async def log():
    while True:
        await asyncio.sleep(4)
        print("i'm alive!")
        print("1", await conn.call("get_version_info"))
        print("3423434234")
        print("2", await conn.call("get_status"))
        print("3", await conn.call("get_login_info"))
        # print(await avilla.get_account("208924405").call("groupList", {"__method__": "fetch"}))


# t = broadcast.loop.create_task(log())

avilla.launch_manager.launch_blocking(loop=broadcast.loop)
