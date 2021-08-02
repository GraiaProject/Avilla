import asyncio
import traceback
from typing import Any, Dict, List, Union

from aiohttp import ClientSession, ClientWebSocketResponse
from aiohttp.http_websocket import WSMsgType
from yarl import URL

from avilla.network.client import AbstractHttpClient, AbstractWebsocketClient
from avilla.utilles.transformer import OriginProvider


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

    async def post(
        self, url: URL, data: bytes, json: Union[Dict, List], *args, **kwargs
    ) -> OriginProvider[bytes]:
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

    def __init__(self, session: ClientSession = None):
        self.session = session or ClientSession()
        super().__init__()

    async def connection_handler(self, id: str, url: URL, *args, **kwargs):
        async with self.session.ws_connect(url, *args, **kwargs) as ws:
            self.connections[id] = ws
            self.cb_connection_created.setdefault(id, [])
            self.cb_connection_closed.setdefault(id, [])
            self.cb_data_received.setdefault(id, [])

            for i in self.cb_connection_created[id]:
                i(self, id)

            async for message in ws:
                if ws.closed:
                    try:
                        for i in self.cb_connection_closed[id]:
                            i(self, id)
                    except Exception:
                        traceback.print_exc()
                if message.type == WSMsgType.TEXT or message.type == WSMsgType.BINARY:
                    try:
                        for i in self.cb_data_received[id]:
                            await i(self, id, message.data)
                    except Exception:
                        traceback.print_exc()

    def connect(self, url: URL, *args, **kwargs) -> None:
        return asyncio.get_running_loop().create_task(
            self.connection_handler(
                kwargs.get("account") or self.gen_conn_id(),
                url,
                *args,
                **{k: v for k, v in kwargs.items() if k != "account"},
            )
        )

    async def close(self, connection_id: str, code: int) -> None:
        if connection_id not in self.connections:
            raise ValueError("connection id doesn't exist.")
        await self.connections[connection_id].close(code=code)

    async def send(self, connection_id: str, data: bytes) -> None:
        if connection_id not in self.connections:
            raise ValueError("connection id doesn't exist.")
        await self.connections[connection_id].send_bytes(data)

    async def send_text(self, connection_id: str, text: str) -> None:
        if connection_id not in self.connections:
            raise ValueError("connection id doesn't exist.")
        await self.connections[connection_id].send_str(text)

    async def send_json(self, connection_id: str, data: Dict[str, Any]) -> None:
        if connection_id not in self.connections:
            raise ValueError("connection id doesn't exist.")
        await self.connections[connection_id].send_json(data)

    async def is_closed(self, connection_id: str) -> bool:
        if connection_id not in self.connections:
            raise ValueError("connection id doesn't exist.")
        return self.connections[connection_id].closed
