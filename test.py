import asyncio
from inspect import unwrap
from aiohttp.client import ClientSession
from loguru import logger
from avilla.core.launch import LaunchComponent
from avilla.core.stream import Stream
from avilla.core.utilles.mock import LaunchMock
from avilla.core.service.aiohttp import AiohttpClient, AiohttpService
from avilla.core.service.common import DataReceived, HttpClient, PostConnected, WebsocketClient, content_read, httpstatus_get, send_netmsg
from avilla.core.transformers import u8_string, json_decode
import random

session = ClientSession()

mocker = LaunchMock(
    {},
    [AiohttpService(session)],
)


async def mainline_test():
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
                await session.execute(send_netmsg(r))
                await asyncio.sleep(1)

        asyncio.create_task(task())
        await asyncio.sleep(20)


mocker.new_launch_component("test.main", mainline_test)
mocker.launch_blocking()
