import asyncio
from inspect import unwrap
from aiohttp.client import ClientSession
from loguru import logger
from avilla.core.launch import LaunchComponent
from avilla.core.service.session import BehaviourSession
from avilla.core.stream import Stream
from avilla.core.utilles.mock import LaunchMock
from avilla.core.service.aiohttp import AiohttpClient, AiohttpService
from avilla.core.service.common.activities import content_read, set_header, get_status, respond, send
from avilla.core.service.common.behaviours import PostConnected, DataReceived
from avilla.core.service.common.http import HttpClient, HttpServer, WebsocketClient
from avilla.core.service.starlette import StarletteService
from avilla.core.service.uvicorn import UvicornService
from avilla.core.transformers import u8_string, json_decode
import random
from starlette.responses import PlainTextResponse

session = ClientSession()

mocker = LaunchMock(
    {},
    [
        StarletteService(),
        UvicornService("127.0.0.1", 12680),
        AiohttpService()
    ],
)


async def mainline_test1(_):
    http_interface: HttpClient = mocker.get_interface(HttpClient)
    print(http_interface)
    async with http_interface.get("https://httpbin.org/anything") as session:
        content_stream: "Stream[bytes]" = Stream(await session.execute(content_read))
        r = await (content_stream | u8_string | json_decode())
        print(r)

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
        await asyncio.sleep(20)


async def mainline_test(_):
    http_server = mocker.get_interface(HttpServer)

    async with http_server.http_listen("/", ['get']) as session:
        @session.expand(DataReceived)
        async def on_data(interface, session: BehaviourSession, stat: dict, data: Stream[bytes]):
            await session.execute_all(
                respond(PlainTextResponse("OK!!!")),
                set_header("Content-Type", "text/plain"),
                set_header("X-Test", "OK"),
            )

        session.prepared()
        await asyncio.sleep(1000)  # 这个会导致 test.py 不会跟随 Ctrl-C(Uvicorn) 退出, 实际中要用 Avilla.sigexit 才行.


mocker.new_launch_component("test.main", set(), mainline_test)
mocker.launch_blocking()
