import asyncio
from typing import Dict, List, Optional, Union
from aiohttp import ClientSession, ClientWebSocketResponse
from aiohttp.http_websocket import WSMsgType
from yarl import URL
from avilla.network.client import AbstractHttpClient, AbstractWebsocketClient
from avilla.utilles.translator import OriginProvider


class AiohttpHttpClient(AbstractHttpClient):
    session: ClientSession

    def __init__(self, session: ClientSession = None):
        self.session = session or ClientSession()
    
    async def request(self, method: str, url: URL, *args, **kwargs) -> OriginProvider[bytes]:
        async with self.session.request(method, url, *args, **kwargs) as response:
            response.raise_for_status()
            return OriginProvider(await response.read())

    async def get(self, url: URL, *args, **kwargs) -> OriginProvider[bytes]:
        async with self.session.get(url, *args, **kwargs) as response:
            response.raise_for_status()
            return OriginProvider(await response.read())
    
    async def post(self, url: URL, data: bytes, json: Union[Dict[str], List], *args, **kwargs) -> OriginProvider[bytes]:
        async with self.session.post(url, data=data, json=json, *args, **kwargs) as response:
            response.raise_for_status()
            return OriginProvider(await response.read())
    
    async def put(self, url: URL, data: bytes, *args, **kwargs) -> None:
        async with self.session.put(url, data=data, *args, **kwargs) as response:
            response.raise_for_status()
    
    async def delete(self, url: URL, *args, **kwargs) -> None:
        async with self.session.delete(url, *args, **kwargs) as response:
            response.raise_for_status()
            
    async def patch(self, url: URL, *args, **kwargs) -> None:
        async with self.session.patch(url, *args, **kwargs) as response:
            response.raise_for_status()

class AiohttpWebsocketClient(AbstractWebsocketClient):
    connections: Dict[str, ClientWebSocketResponse]
    session: ClientSession

    data_queues: Dict[str, asyncio.Future]

    def __init__(self, session: ClientSession = None):
        self.session = session or ClientSession()
        self.data_queues = {}
        super().__init__()

    async def connection_handler(self, id: str, url: URL, *args, **kwargs):
        async with self.session.ws_connect(url, *args, **kwargs) as ws:
            self.connections[id] = ws
            async for message in ws:
                if ws.closed:
                    break
                get_req: Optional[asyncio.Future] = self.data_queues.get(id)
                if get_req and not get_req.done():
                    get_req.set_result(message.data)

    def connect(self, url: URL, *args, **kwargs) -> None:
        asyncio.get_running_loop().create_task(self.connection_handler(url, *args, **kwargs))

    async def close(self, connection_id: str, code: int) -> None:
        if connection_id not in self.connections:
            raise ValueError("connection id doesn't exist.")
        await self.connections[connection_id].close(code=code)

    async def send(self, connection_id: str, data: bytes) -> None:
        if connection_id not in self.connections:
            raise ValueError("connection id doesn't exist.")
        await self.connections[connection_id].send_bytes(data)

    async def send_text(self, connection_id: str, text: str) -> None:
        await self.send(connection_id, text.encode())

    async def recv(self, connection_id: str) -> OriginProvider[bytes]:
        if connection_id not in self.connections:
            raise ValueError("connection id doesn't exist.")
        self.data_queues[connection_id] = asyncio.get_running_loop().create_future()
        data = await self.data_queues[connection_id]
        del self.data_queues[connection_id]
        return OriginProvider(data)

    async def recv_text(self, connection_id: str) -> OriginProvider[str]:
        return OriginProvider((await self.recv(connection_id)).transform().decode())

    async def is_closed(self, connection_id: str) -> bool: 
        if connection_id not in self.connections:
            raise ValueError("connection id doesn't exist.")
        return self.connections[connection_id].closed