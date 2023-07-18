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
from avilla.onebot.v11.protocol import OneBot11Protocol
from avilla.standard.core.message.capability import MessageRevoke

# from graia.amnesia.builtins.aiohttp import AiohttpClientService
from graia.broadcast import Broadcast
from launart import Launart
from test_env import A60_ENDPOINT, A60_MAH_ACCOUNT, A60_MAH_SECRET, A60_SECRET

# richuru1.install()

broadcast = create(Broadcast)
launart = Launart()
protocol = OneBot11Protocol()
service = protocol.service
config = OneBot11WsClientConfig(URL(A60_ENDPOINT), A60_SECRET)
conn = OneBot11WsClientNetworking(protocol, config)
service.connections.append(conn)

platform = Platform(Land("qq"), Abstract("onebot/v11"))


mah = ElizabethProtocol()
conn1 = ElizabethWsClientNetworking(
    mah, ElizabethWsClientConfig(URL("http://localhost:8660/"), A60_MAH_SECRET, A60_MAH_ACCOUNT)
)
mah.service.connections.append(conn1)

console_protocol = ConsoleProtocol()
avilla = Avilla(broadcast, launart, [protocol], message_cache_size=0)

protocol.avilla = avilla


# debug(protocol.isolate.artifacts)
# exit()


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
        print("!", list(avilla.accounts.values())[0].account.__dict__)
        # print(mah.service.account_map)
        # print(await list(avilla.accounts.values())[0].account.connection.call("fetch", "groupList", {}))
        print("!!!!!")
        # async for i in Staff(list(avilla.accounts.values())[0].account).query_entities("land.group.member"):
        #    print(i)
        # print("????????")
        # print(await avilla.get_account("208924405").call("groupList", {"__method__": "fetch"}))


#t = broadcast.loop.create_task(log())

avilla.launch_manager.launch_blocking(loop=broadcast.loop)
