import sys
from avilla.core.account import AbstractAccount
from avilla.core.elements import Image
from avilla.core.resource.local import LocalFileResource
from avilla.core.utilles.selector import Selector

from creart import create
from graia.amnesia.builtins.aiohttp import AiohttpService
from graia.broadcast import Broadcast

from avilla.core import Avilla
from avilla.core.action import IterateMembers, MessageSend
from avilla.core.event.message import MessageReceived
from avilla.core.relationship import Relationship
from avilla.elizabeth.protocol import ElizabethProtocol


def loguru_excepthook(ex_type, ex_value, ex_traceback):
    if ex_type is not None:
        import loguru

        loguru.logger.opt(exception=(ex_type, ex_value, ex_traceback)).error("Unhandled exception")
    else:
        import sys

        sys.__excepthook__(ex_type, ex_value, ex_traceback)


sys.excepthook = loguru_excepthook

protocol = ElizabethProtocol()
broadcast = create(Broadcast)
avilla = Avilla(broadcast, [protocol], [AiohttpService()])


@broadcast.receiver(MessageReceived)
async def on_message_received(event: MessageReceived, rs: Relationship, account: AbstractAccount):
    print(event, rs, rs.ctx.pattern, Selector(mode="exist").member(lambda x: x == "1846913566").match(rs.ctx))
    if Selector.fragment().group("*").member("1846913566").match(rs.ctx):
        # await rs.exec(MessageSend([
        #    "Hello, Avilla!", Image(LocalFileResource("development/photo_2022-07-10_22-12-22.jpg"))
        # ]))
        t = rs.complete(Selector().friend("1846913566"))
        rs2 = await account.get_relationship(t)
        await rs2.exec(MessageSend([
            "Hello, Avilla!", Image(LocalFileResource("development/photo_2022-07-10_22-12-22.jpg"))
        ]))


avilla.launch_manager.launch_blocking(loop=broadcast.loop)
