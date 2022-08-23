import asyncio
import sys

from creart import create
from graia.amnesia.builtins.aiohttp import AiohttpClientService
from graia.broadcast import Broadcast

from avilla.core.account import AbstractAccount
from avilla.core.action import MessageSend
from avilla.core.application import Avilla
from avilla.core.elements import Picture
from avilla.core.event.message import MessageReceived
from avilla.core.message import Message, MessageTrait
from avilla.core.relationship import Relationship
from avilla.core.resource import LocalFileResource
from avilla.core.utilles.selector import DynamicSelector, Selector
from avilla.elizabeth.connection.config import WebsocketClientConfig
from avilla.elizabeth.protocol import ElizabethProtocol


def loguru_excepthook(ex_type, ex_value, ex_traceback):
    if ex_type is not None:
        import loguru

        loguru.logger.opt(exception=(ex_type, ex_value, ex_traceback)).error("Unhandled exception")
    else:
        import sys

        sys.__excepthook__(ex_type, ex_value, ex_traceback)


sys.excepthook = loguru_excepthook

protocol = ElizabethProtocol(WebsocketClientConfig("1779309090", "testafafv4fv34v34g3y45"))
broadcast = create(Broadcast)
avilla = Avilla(broadcast, [protocol], [AiohttpClientService()])


@broadcast.receiver(MessageReceived)
async def on_message_received(event: MessageReceived, rs: Relationship, account: AbstractAccount):
    print(event, rs, rs.ctx.pattern, DynamicSelector(mode="exist").member(lambda x: x == "1846913566").match(rs.ctx))
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
        r = await rs.send_message(
            [
                "Hello, Avilla!",
                Picture(LocalFileResource("development/photo_2022-07-10_22-12-22.jpg")),
                "\n本消息将于 10s 后撤回",
            ]
        )
        await asyncio.sleep(10)
        c = await rs.cast(MessageTrait).revoke(r)
        # print(rs.complete(DynamicSelector().group("*")))
        # async for i in rs.query(DynamicSelector().land(rs.land).group("*").member("*")):
        #    print(i)


avilla.launch_manager.launch_blocking(loop=broadcast.loop)
