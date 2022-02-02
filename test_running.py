import asyncio
import traceback

from aiohttp import ClientSession
from graia.broadcast import Broadcast
from yarl import URL

from avilla.core import Avilla
from avilla.core.elements import Image, Notice, Text
from avilla.core.event.message import MessageReceived
from avilla.core.execution import MessageSend
from avilla.core.message import Message
from avilla.core.relationship import CoreSupport, Relationship
from avilla.core.selectors import entity, mainline, resource
from avilla.core.utilles import Defer
from avilla.io.common.storage import CacheStorage
from avilla.io.core.aiohttp import AiohttpService
from avilla.io.core.starlette import StarletteService
from avilla.io.core.uvicorn import UvicornService
from avilla.onebot.config import OnebotWsClientConfig, OnebotWsServerConfig
from avilla.onebot.protocol import OnebotProtocol
from avilla.onebot.service import OnebotService

loop = asyncio.new_event_loop()
broadcast = Broadcast(loop=loop)
avilla = Avilla(
    broadcast=broadcast,
    protocols=[OnebotProtocol],
    services=[
        AiohttpService(ClientSession(loop=loop)),
        StarletteService(),
        UvicornService("localhost", 5290),
    ],
    config={OnebotService: {entity.account["1779309090"]: OnebotWsServerConfig(access_token=None)}},
)


@broadcast.receiver(MessageReceived)
async def hello_world(
    event: MessageReceived,
    rs: Relationship[CoreSupport],
    message: Message,
    protocol: OnebotProtocol,
    defer: Defer,
):
    try:
        print(message.sender.get_entity_value(), message.sender)
        if message.sender.get_entity_value() == "1846913566":
            print("?????")
            #print(await rs.meta.get("mainline.name"))
            #print(await rs.meta.get("mainline.name"))
            cache = avilla.get_interface(CacheStorage)
            print(await cache.keys())
            print(defer.defers)
            #await rs.exec(MessageSend(message.content)).to(rs.mainline)
            await rs.exec(MessageSend([
                Text("hello world"),
            ], reply=message))
    except:
        traceback.print_exc()


loop.run_until_complete(avilla.launch())
