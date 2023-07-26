import asyncio

from creart import create
from yarl import URL

from avilla.console.protocol import ConsoleProtocol
from avilla.core import Avilla, Context, MessageReceived
from avilla.core.elements import Notice, Picture
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.resource import LocalFileResource
from avilla.elizabeth.connection.ws_client import ElizabethWsClientConfig, ElizabethWsClientNetworking
from avilla.elizabeth.protocol import ElizabethProtocol
from avilla.onebot.v11.net.ws_client import OneBot11WsClientConfig, OneBot11WsClientNetworking
from avilla.onebot.v11.net.ws_server import OneBot11WsServerConfig, OneBot11WsServerNetworking
from avilla.onebot.v11.protocol import OneBot11Protocol
from avilla.standard.core.message.capability import MessageRevoke
from graia.amnesia.builtins.asgi import UvicornASGIService

# from graia.amnesia.builtins.aiohttp import AiohttpClientService
from graia.broadcast import Broadcast
from launart import Launart
from test_env import A60_ENDPOINT, A60_MAH_ACCOUNT, A60_MAH_SECRET, A60_SECRET

# richuru1.install()

broadcast = create(Broadcast)
launart = Launart()
protocol = OneBot11Protocol()
service = protocol.service

#config = OneBot11WsClientConfig(URL(A60_ENDPOINT), A60_SECRET)
#conn = OneBot11WsClientNetworking(protocol, config)
#service.connections.append(conn)

config = OneBot11WsServerConfig("/ob", A60_SECRET)
net = OneBot11WsServerNetworking(protocol, config)
service.connections.append(net)

mah = ElizabethProtocol()
conn1 = ElizabethWsClientNetworking(
    mah, ElizabethWsClientConfig(URL("http://localhost:8660/"), A60_MAH_SECRET, A60_MAH_ACCOUNT)
)
mah.service.connections.append(conn1)

console_protocol = ConsoleProtocol()
avilla = Avilla(broadcast, launart, [protocol, console_protocol], message_cache_size=0)

protocol.avilla = avilla

launart.add_component(UvicornASGIService(
    "127.0.0.1", 9090
))

@broadcast.receiver(MessageReceived)
async def on_message_received(cx: Context, event: MessageReceived):
    # debug(cx.artifacts.maps)
    #print(cx.endpoint, cx.scene, cx.client, cx.self, cx.account)
    if cx.client.follows("::group.member(1846913566)"):
        msg = await cx.scene.send_message(
            [
                "Hello, Avilla!",
                Notice(cx.scene.member("1846913566")),
                Picture(LocalFileResource("D:/kaf.webp")),
            ]
        )
        await asyncio.sleep(3)
        # print(await conn1.call("get", "friendList"))
        await cx[MessageRevoke.revoke](msg)
    elif cx.client.follows("::land(console).console(console_user)"):
        await cx.scene.send_message("Hello, Console User!")



async def log():
    while True:
        await asyncio.sleep(5)
        print("?")
        print(avilla.launch_manager.get_component("asgi.service/uvicorn").middleware.mounts)
        
#t = broadcast.loop.create_task(log())

avilla.launch_manager.launch_blocking(loop=broadcast.loop)
