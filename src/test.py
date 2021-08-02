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
from avilla.utilles.depends import useCtx, useCtxId, useCtxProfile
from avilla.builtins.elements import PlainText

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
    headless_decorators=[useCtx(Entity), useCtxProfile(Entity, MemberProfile), useCtxId(Entity, "1846913566")],
)
async def event_receiver(rs: Relationship, message: MessageEvent):
    await rs.exec(MessageSend(MessageChain.create([PlainText("不知不觉中所隐藏的\n真实的心声 让我听见它放声回响吧\n就算你熟视无睹\n可它的确就在那里")])))


loop.run_until_complete(avilla.launch())
loop.run_forever()
