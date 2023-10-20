import asyncio

from creart import create

from avilla.console.protocol import ConsoleProtocol
from avilla.core import Avilla, Context, MessageReceived
from avilla.core.elements import Notice, Picture
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.resource import LocalFileResource
from avilla.elizabeth.protocol import ElizabethProtocol, ElizabethConfig
from avilla.onebot.v11.protocol import OneBot11Protocol, OneBot11ReverseConfig
from avilla.standard.core.message.capability import MessageRevoke, MessageSend
from graia.amnesia.builtins.asgi import UvicornASGIService

# from graia.amnesia.builtins.aiohttp import AiohttpClientService
from graia.broadcast import Broadcast
from launart import Launart
from test_env import A60_ENDPOINT, A60_MAH_ACCOUNT, A60_MAH_SECRET, A60_SECRET

from devtools import debug

# richuru1.install()

broadcast = create(Broadcast)
launart = Launart()


#ob_config = OneBot11ReverseConfig("/ob", "dfawdfafergergeaar")
#ob = OneBot11Protocol().configure(ob_config)
#mah_config = ElizabethConfig(A60_MAH_ACCOUNT, "localhost", 8660, A60_MAH_SECRET)
#mah = ElizabethProtocol().configure(mah_config)
console_protocol = ConsoleProtocol()
#
avilla = Avilla(launch_manager=launart, broadcast=broadcast, message_cache_size=0)
#
avilla.apply_protocols(console_protocol)
#debug(ob.artifacts)

launart.add_component(UvicornASGIService("127.0.0.1", 9090))

import sys

#sys.setrecursionlimit(200)

from avilla.core.ryanvk.collector.context import ContextCollector
from graia.ryanvk import OverridePerformEntity, SupportsCollect
from graia.amnesia.message import MessageChain
from avilla.core.selector import Selector

from graia.ryanvk.typing import P, R

def x(a: SupportsCollect[P, R]) -> SupportsCollect[P, R]:
    return a

class TestPerform((m := ContextCollector())._):
    @MessageSend.send.override(m, target="::friend")
    async def s2(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        return await self.s2.super(target, message + "2cefarfr444", reply=reply)


class TestPerform1((n := ContextCollector())._):
    @MessageSend.send.override(n, target="::friend")
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
    print(cx.endpoint, cx.scene, cx.client, cx.self, cx.account)
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
    elif cx.client.follows("::user(console)"):
        await cx.scene.send_message("Hello, Console User!")
    elif cx.client.follows("::friend"):
        await cx.scene.send_message("2222222222")


async def log():
    while True:
        await asyncio.sleep(5)
        print("?")
        print(avilla.launch_manager.get_component(UvicornASGIService).middleware.mounts)


# t = broadcast.loop.create_task(log())

from devtools import debug

from graia.saya import Saya
from creart import it

saya = it(Saya)

with saya.module_context():
    saya.require("avilla.plugins.hello")
    saya.require("avilla.plugins.echo")


avilla.launch_manager.launch_blocking(loop=broadcast.loop)
