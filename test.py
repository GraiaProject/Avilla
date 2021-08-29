import asyncio
import logging
from aiohttp.client import ClientSession
from graia.broadcast import Broadcast
from yarl import URL
from avilla.core import Avilla
from avilla.core.builtins.middlewares import useTarget
from avilla.core.builtins.profile import MemberProfile
from avilla.core.entity import Entity
from avilla.core.event.message import MessageEvent
from avilla.core.execution.message import MessageSend
from avilla.core.group import GroupPtr
from avilla.core.message.chain import MessageChain
from avilla.core.network.clients.aiohttp import AiohttpWebsocketClient
from avilla.onebot.ability import ABILITIES
from avilla.onebot.config import OnebotConfig, WebsocketCommunication
from avilla.onebot.protocol import OnebotProtocol
from avilla.core.relationship import Relationship
from avilla.core.tools.literature import Literature
from avilla.core.tools.template import Template
from avilla.core.utilles.depends import useCtx, useCtxId, useCtxProfile, useGroupInMemberProfile
from avilla.core.builtins.elements import Image, Notice, Text

loop = asyncio.get_event_loop()
broadcast = Broadcast(loop=loop)
session = ClientSession(loop=loop)
avilla = Avilla(
    broadcast,
    OnebotProtocol,
    {"ws": AiohttpWebsocketClient(session)},
    {
        OnebotProtocol: OnebotConfig(
            access_token="avilla-test",
            bot_id=208924405,
            communications={"ws": WebsocketCommunication(api_root=URL("ws://127.0.0.1:6700/"))},
        )
    },
)

logging.basicConfig(
    format="[%(asctime)s][%(levelname)s]: %(message)s",
    level=logging.INFO,
)


@broadcast.receiver(
    MessageEvent,
    decorators=[useCtx(Entity), useCtxProfile(Entity, MemberProfile), useGroupInMemberProfile("941310484")],
)
async def event_receiver(rs: Relationship, message: MessageChain):
    print(message.as_display())
    await rs.exec(
        MessageSend(Template("$sender, 这是 Template 测试, $sender").render(sender=Notice(rs.ctx.id))),
        useTarget(GroupPtr("372286357"))
    )


loop.run_until_complete(avilla.launch())
loop.run_forever()
