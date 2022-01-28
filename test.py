import asyncio
from inspect import unwrap
from typing import Optional
from aiohttp.client import ClientSession
from loguru import logger
from sqlalchemy import engine
from sqlmodel import Field, SQLModel, select
from avilla.core import Avilla
from avilla.core.launch import LaunchComponent
from avilla.core.service.session import BehaviourSession
from avilla.core.service.sqlmodel import EngineProvider, SqlmodelService
from avilla.core.stream import Stream
from avilla.core.utilles.mock import LaunchMock
from avilla.io.core.aiohttp import AiohttpClient, AiohttpService
from avilla.core.service.common.activities import content_read, set_header, get_status, respond, send
from avilla.core.service.common.behaviours import PostConnected, DataReceived
from avilla.core.service.common.http import HttpClient, HttpServer, WebsocketClient
from avilla.io.core.starlette import StarletteService
from avilla.io.core.uvicorn import UvicornService
from avilla.core.transformers import u8_string, json_decode
import random
from starlette.responses import PlainTextResponse
from sqlmodel.ext.asyncio.session import AsyncSession
mocker = LaunchMock(
    {},
    [
        StarletteService(),
        #UvicornService("127.0.0.1", 12680),
        AiohttpService(),
        SqlmodelService("sqlite+aiosqlite://")
    ],
)


async def test(_):
    http_interface: HttpClient = mocker.get_interface(HttpClient)
    print(http_interface)
    async with http_interface.get("https://httpbin.org/anything") as session:
        content_stream = await session.execute(content_read)
        r = await (content_stream | u8_string | json_decode())
        print(r)

    """
    ws = mocker.get_interface(WebsocketClient)
    async with ws.websocket_connect("ws://ws.ifelse.io/") as session:
        @session.expand(PostConnected)
        async def on_connected(interface, session, stat):
            stat['e'] = random.random()
    
        @session.expand(DataReceived)
        async def on_data(interface, session, stat, data):
            stat['e'] += random.random()
            logger.debug(f"{stat} {data}")

        session.prepared()
        async def task():
            for i in range(20):
                r = f"send {i} {random.random()}"
                logger.debug(r)
                await session.execute(send(r))
                await asyncio.sleep(1)

        asyncio.create_task(task())
        await asyncio.sleep(20)"""


async def mainline_test(_):
    http_server = mocker.get_interface(HttpServer)

    async with http_server.http_listen("/", ["get"]) as session:

        @session.expand(DataReceived)
        async def on_data(interface, session: BehaviourSession, stat: dict, data: Stream[bytes]):
            await session.execute_all(
                respond(PlainTextResponse("OK!!!")),
                set_header("Content-Type", "text/plain"),
                set_header("X-Test", "OK"),
            )

        session.prepared()
        await mocker.sigexit.wait()


async def statusbar_test(_):
    await asyncio.sleep(1)


async def mainline_test2(_):
    await asyncio.sleep(100)


class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None


async def sqlmodel_test(avilla: LaunchMock):
    engine = avilla.get_interface(EngineProvider).get()
    async with AsyncSession(engine) as session:
        session.add(Hero(name="John", secret_name="Doe", age=20))
        session.add(Hero(name="Jane", secret_name="Doe", age=20))
        session.add(Hero(name="Jack", secret_name="Doe", age=20))   
        await session.commit()

    async with AsyncSession(engine) as session:
        heroes = await session.execute(select(Hero))
        for hero in heroes:
            print(hero)
    

mocker.new_launch_component(
    "test.main",
    set(),
    #mainline=mainline_test,
    # mainline=mainline_test2,
    mainline=sqlmodel_test
    #prepare=statusbar_test,
)


mocker.launch_blocking()
