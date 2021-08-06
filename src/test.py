import asyncio
import logging
from pathlib import Path
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
from avilla.provider import FileProvider
from avilla.relationship import Relationship
from avilla.utilles.depends import useCtx, useCtxId, useCtxProfile, useGroupInMemberProfile
from avilla.builtins.elements import Image, PlainText

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
    headless_decorators=[
        useCtx(Entity),
        useCtxProfile(Entity, MemberProfile),

        useCtxId(Entity, "1846913566"),
        useGroupInMemberProfile("1137320960", "941310484")
    ]
)
async def event_receiver(rs: Relationship, message: MessageChain):
    print(message.as_display())
    if not message.startswith("/test"):
        return
    await rs.exec(MessageSend(MessageChain.create([
        Image(FileProvider(Path(r"D:\pixiv\69417507_p0.png")))
    ])))

loop.run_until_complete(avilla.launch())
loop.run_forever()
