import asyncio
from aiohttp import ClientSession
from graia.broadcast import Broadcast
from avilla.core.elements import Image, Notice, Text
from avilla.core.execution import MessageSend
from avilla.core.message import Message
from avilla.core.relationship import Relationship
from yarl import URL
from avilla.core import Avilla
from avilla.core.event.message import MessageReceived
from avilla.core.selectors import entity, mainline, resource
from avilla.io.core.aiohttp import AiohttpService
from avilla.onebot.config import OnebotWsClientConfig
from avilla.onebot.protocol import OnebotProtocol
from avilla.onebot.service import OnebotService

loop = asyncio.new_event_loop()
broadcast = Broadcast(loop=loop)
avilla = Avilla(
    broadcast=broadcast,
    protocols=[OnebotProtocol],
    services=[
        AiohttpService(ClientSession(loop=loop)),
    ],
    config={
        OnebotService: {
            entity.account['1779309090']: OnebotWsClientConfig(
                url=URL("ws://localhost:6700/"),
                access_token=None
            )
        }
    }
)

@broadcast.receiver(MessageReceived)
async def hello_world(event: MessageReceived, rs: Relationship, message: Message):
    if message.mainline['group'] == "931587979" and message.sender['member'] == "1846913566":
        await rs.exec(MessageSend([
            Text("hello world"),
        ], reply=message)).to(rs.mainline)


loop.run_until_complete(avilla.launch())