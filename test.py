import asyncio

from creart import create

# from avilla.core._vendor.graia.amnesia.builtins.aiohttp import AiohttpClientService
from graia.broadcast import Broadcast
from yarl import URL

from avilla.console.protocol import ConsoleProtocol
from avilla.core import Avilla, Context, MessageReceived
from avilla.core._vendor.graia.amnesia.builtins.asgi import UvicornASGIService
from avilla.core._vendor.launart import Launart
from avilla.core.elements import Notice, Picture
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.resource import LocalFileResource
from avilla.elizabeth.connection.ws_client import ElizabethWsClientConfig, ElizabethWsClientNetworking
from avilla.elizabeth.protocol import ElizabethProtocol
from avilla.onebot.v11.net.ws_client import OneBot11WsClientConfig, OneBot11WsClientNetworking
from avilla.onebot.v11.net.ws_server import OneBot11WsServerConfig, OneBot11WsServerNetworking
from avilla.onebot.v11.protocol import OneBot11Protocol
from avilla.standard.core.message.capability import MessageRevoke, MessageSend
from test_env import A60_ENDPOINT, A60_MAH_ACCOUNT, A60_MAH_SECRET, A60_SECRET

# richuru1.install()

broadcast = create(Broadcast)
launart = Launart()
protocol = OneBot11Protocol()
service = protocol.service

# config = OneBot11WsClientConfig(URL(A60_ENDPOINT), A60_SECRET)
# conn = OneBot11WsClientNetworking(protocol, config)
# service.connections.append(conn)

config = OneBot11WsServerConfig("/ob", "dfawdfafergergeaar")
net = OneBot11WsServerNetworking(protocol, config)
service.connections.append(net)

mah = ElizabethProtocol()
conn1 = ElizabethWsClientNetworking(
    mah, ElizabethWsClientConfig(URL("http://localhost:8660/"), A60_MAH_SECRET, A60_MAH_ACCOUNT)
)
mah.service.connections.append(conn1)

console_protocol = ConsoleProtocol()

avilla = Avilla(launch_manager=launart, broadcast=broadcast, message_cache_size=0)

avilla.apply_protocols(protocol)

launart.add_component(UvicornASGIService("127.0.0.1", 9090))

import sys

sys.setrecursionlimit(200)

from avilla.core._vendor.graia.amnesia.message import MessageChain
from avilla.core.ryanvk.collector.context import ContextCollector
from avilla.core.ryanvk.descriptor.base import OverridePerformEntity
from avilla.core.selector import Selector


class TestPerform((m := ContextCollector())._):
    @MessageSend.send.override(m, "::friend")
    async def s2(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        return await self.s2.super(target, message + "2cefarfr444", reply=reply)


class TestPerform1((n := ContextCollector())._):
    @MessageSend.send.override(n, "::friend")
    async def s2(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        return await self.s2.super(target, message + "2cefarfr444", reply=reply)


@broadcast.receiver(MessageReceived)
async def on_message_received(cx: Context, event: MessageReceived):
    # debug(cx.artifacts.maps)
    # print(cx.endpoint, cx.scene, cx.client, cx.self, cx.account)
    cx.staff.inject(TestPerform)
    cx.staff.inject(TestPerform1)
    if cx.client.follows("::group.member(1846913566)"):
        msg = await cx.scene.send_message(
            [
                "Hello, Avilla!",
                Notice(cx.scene.member("1846913566")),
                Picture("D:/kaf.webp"),
            ]
        )
        await asyncio.sleep(3)
        # print(await conn1.call("get", "friendList"))
        await cx[MessageRevoke.revoke](msg)
    elif cx.client.follows("::console(console_user)"):
        await cx.scene.send_message("Hello, Console User!")
    elif cx.client.follows("::friend"):
        await cx.scene.send_message("2222222222")


async def log():
    while True:
        await asyncio.sleep(5)
        print("?")
        print(avilla.launch_manager.get_component("asgi.service/uvicorn").middleware.mounts)


# t = broadcast.loop.create_task(log())

from devtools import debug

from avilla.core.ryanvk._runtime import ARTIFACT_COLLECTIONS

avilla.launch_manager.launch_blocking()
