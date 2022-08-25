import asyncio
from datetime import timedelta
import sys
from avilla.core.cell.cells import Privilege
from avilla.core.skeleton.message import MessageTrait
from avilla.core.skeleton.privilege import Mute

from creart import create
from graia.amnesia.builtins.aiohttp import AiohttpClientService
from graia.broadcast import Broadcast

from avilla.core.account import AbstractAccount
#from avilla.core.action import MessageSend
from avilla.core.application import Avilla
from avilla.core.elements import Picture
from avilla.core.event.message import MessageReceived
from avilla.core.message import Message
from avilla.core.relationship import Relationship
from avilla.core.resource import LocalFileResource
from avilla.core.utilles.selector import DynamicSelector, Selector
from avilla.elizabeth.connection.config import WebsocketClientConfig
from avilla.elizabeth.protocol import ElizabethProtocol


protocol = ElizabethProtocol(WebsocketClientConfig("1779309090", "testafafv4fv34v34g3y45"))
broadcast = create(Broadcast)
avilla = Avilla(broadcast, [protocol], [AiohttpClientService()])


@broadcast.receiver(MessageReceived)
async def on_message_received(event: MessageReceived, rs: Relationship, account: AbstractAccount):
    print(event, rs, rs.ctx.pattern, DynamicSelector(mode="exist").member(lambda x: x == "1846913566").match(rs.ctx))
    print(await rs.pull(Privilege, rs.ctx))
    if DynamicSelector.fragment().group("*").member("1846913566").match(rs.ctx):
        # await rs.exec(MessageSend([
        #    "Hello, Avilla!", Image(LocalFileResource("development/photo_2022-07-10_22-12-22.jpg"))
        # ]))
        # t = rs.complete(Selector().friend("1846913566"))
        # print(t)
        # rs2 = await account.get_relationship(t)
        a = event.message.content.get(Picture)
        print(a, event.message.content)
        if a:
            b = await rs.fetch(a[0].resource)
            print("pulled!", len(list(b)))
        #r = await rs.send_message(
        #    [
        #        "Hello, Avilla!",
        #        Picture(LocalFileResource("development/photo_2022-07-10_22-12-22.jpg")),
        #        "\n本消息将于 10s 后撤回",
        #    ]
        #)
        #print(await rs.cast(Mute).mute(rs.mainline.copy().member("3542335634"), timedelta(minutes=10)))
        #await asyncio.sleep(2)
        #print(await rs.cast(Mute).unmute(rs.mainline.copy().member("3542335634")))
        #c = await rs.cast(MessageTrait).revoke(r)
        #print("1")
        #async for i in rs.query(DynamicSelector().group("*").member("*")):
        #    print(i)
        #print("2")
        # print(rs.complete(DynamicSelector().group("*")))
        # async for i in rs.query(DynamicSelector().land(rs.land).group("*").member("*")):
        #    print(i)


avilla.launch_manager.launch_blocking(loop=broadcast.loop)
