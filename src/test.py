import asyncio
import logging
from aiohttp.client import ClientSession
from graia.broadcast import Broadcast
from yarl import URL
from avilla import Avilla
from avilla.builtins.profile import MemberProfile
from avilla.entity import Entity
from avilla.event.message import MessageEvent
from avilla.execution.message import MessageSend
from avilla.message.chain import MessageChain
from avilla.network.clients.aiohttp import AiohttpWebsocketClient
from avilla.onebot.config import OnebotConfig, WebsocketCommunication
from avilla.onebot.protocol import OnebotProtocol
from avilla.relationship import Relationship
from avilla.tools.literature import Literature
from avilla.tools.template import Template
from avilla.utilles.depends import useCtx, useCtxId, useCtxProfile, useGroupInMemberProfile
from avilla.builtins.elements import Notice, PlainText

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
    decorators=[
        useCtx(Entity),
        useCtxProfile(Entity, MemberProfile),

        useCtxId(Entity, "1846913566"),
        useGroupInMemberProfile("1137320960", "941310484")
    ],
    dispatchers=[
        Literature("/test")
    ]
)
async def event_receiver(rs: Relationship, message: MessageChain):
    print(message.as_display())
    await rs.exec(MessageSend(Template("$sender, 这是 Template 测试, $sender").render(
        sender=Notice(rs.ctx.id)
    )))


loop.run_until_complete(avilla.launch())
loop.run_forever()
