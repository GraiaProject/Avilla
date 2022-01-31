import asyncio
from contextlib import asynccontextmanager
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    Union,
)

from aiohttp import ClientResponse, ClientSession, WSMsgType
from aiohttp.client_ws import ClientWebSocketResponse
from aiohttp.helpers import BasicAuth, ProxyInfo
from loguru import logger
from yarl import URL

from avilla.core.launch import LaunchComponent
from avilla.core.selectors import entity as entity_selector
from avilla.core.service import Service
from avilla.core.service.session import BehaviourSession
from avilla.core.stream import Stream
from avilla.io.common.http import (
    HTTP_METHODS,
    HttpClient,
    HttpClientResponse,
    ProxySetting,
    WebsocketClient,
    WebsocketConnection,
)


def proxysetting_transform(proxy_setting: ProxySetting) -> ProxyInfo:
    return ProxyInfo(
        URL(f"{proxy_setting.protocol}://{proxy_setting.host}:{proxy_setting.port}"),
        BasicAuth(proxy_setting.auth_username, proxy_setting.auth_password)
        if proxy_setting.auth_username and proxy_setting.auth_password
        else None,
    )


class AiohttpHttpResponse(HttpClientResponse):
    session: ClientSession
    response: ClientResponse

    def __init__(self, session: ClientSession, response: ClientResponse):
        self.session = session
        self.response = response

    @property
    def url(self) -> URL:
        return self.response.url

    @property
    def status(self) -> int:
        return self.response.status

    async def read(self) -> Stream[bytes]:
        return Stream(await self.response.read())

    async def cookies(self) -> Dict[str, str]:
        return {k: str(v) for k, v in self.response.cookies.items()}

    async def headers(self) -> Dict[str, str]:
        return {k: str(v) for k, v in self.response.headers.items()}

    async def close(self):
        self.response.close()

    def raise_for_status(self):
        self.response.raise_for_status()


class AiohttpWebsocketClientConnection(WebsocketConnection):
    server_mode = False
    ready: asyncio.Event

    session: ClientSession
    response: Optional[ClientWebSocketResponse]

    connected_callbacks: List[Callable[["AiohttpWebsocketClientConnection"], Awaitable[Any]]]
    received_callbacks: List[Callable[["AiohttpWebsocketClientConnection", Stream[bytes]], Awaitable[Any]]]
    error_callbacks: List[Callable[["AiohttpWebsocketClientConnection", Exception], Awaitable[Any]]]
    close_callbacks: List[Callable[["AiohttpWebsocketClientConnection"], Awaitable[Any]]] = []

    def __init__(self, session: ClientSession):
        self.session = session
        self.ready = asyncio.Event()
        self.connected_callbacks = []
        self.received_callbacks = []
        self.error_callbacks = []
        self.close_callbacks = []

    async def accept(self) -> None:
        raise NotImplementedError

    async def send(self, data: Union[Stream[Union[bytes, str, dict, list]], bytes, str, dict, list]) -> None:
        if not self.response:
            raise RuntimeError("Websocket connection not prepared")
        if isinstance(data, Stream):
            data = await data.unwrap()
        if isinstance(data, bytes):
            await self.response.send_bytes(data)
        elif isinstance(data, str):
            await self.response.send_str(data)
        elif isinstance(data, (dict, list)):
            await self.response.send_json(data)
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")
        logger.debug(f"websocket send: {data}")

    async def receive(self) -> Stream[bytes]:
        if not self.response:
            raise RuntimeError("Websocket connection not prepared")
        return Stream(await self.response.receive_bytes())

    async def ping(self) -> None:
        if not self.response:
            raise RuntimeError("Websocket connection not prepared")
        await self.response.ping()

    async def pong(self) -> None:
        if not self.response:
            raise RuntimeError("Websocket connection not prepared")
        await self.response.pong()

    async def close(self, code: int = 1000, message: bytes = b"") -> None:
        if not self.response:
            raise RuntimeError("Websocket connection not prepared")
        await self.response.close(code=code, message=message)

    @property
    def status(self) -> int:
        return 1

    def raise_for_status(self):
        pass

    def on_connected(self, callback: Callable[["WebsocketConnection"], Awaitable[Any]]):
        self.connected_callbacks.append(callback)
        return callback

    def on_received(
        self, callback: Callable[["AiohttpWebsocketClientConnection", Stream[bytes]], Awaitable[Any]]
    ):
        self.received_callbacks.append(callback)
        return callback

    def on_close(self, callback: Callable[["WebsocketConnection"], Awaitable[Any]]):
        self.close_callbacks.append(callback)
        return callback

    def on_error(self, callback: Callable[["WebsocketConnection", Exception], Awaitable[Any]]):
        self.error_callbacks.append(callback)
        return callback


class AiohttpClient(HttpClient, WebsocketClient):
    aiohttp_session: ClientSession

    def __init__(self, service: "AiohttpService", aiohttp_session: ClientSession) -> None:
        self.service = service
        self.aiohttp_session = aiohttp_session
        super().__init__()

    @asynccontextmanager
    async def request(
        self,
        method: "HTTP_METHODS",
        url: Union[str, URL],
        headers: Dict[str, str] = None,
        data: Union[str, bytes] = None,
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        async with self.aiohttp_session.request(
            method,
            url,
            headers=headers,
            data=data,
            proxy=proxysetting_transform(proxy) if proxy is not None else None,
        ) as response:
            yield AiohttpHttpResponse(self.aiohttp_session, response)

    @asynccontextmanager
    async def get(
        self,
        url: Union[str, URL],
        headers: Dict[str, str] = None,
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        async with self.aiohttp_session.get(
            url, headers=headers, proxy=proxysetting_transform(proxy) if proxy is not None else None
        ) as response:
            yield AiohttpHttpResponse(self.aiohttp_session, response)

    @asynccontextmanager
    async def post(
        self,
        url: Union[str, URL],
        data: Union[str, bytes],
        headers: Dict[str, str] = None,
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        async with self.aiohttp_session.post(
            url,
            headers=headers,
            data=data,
            proxy=proxysetting_transform(proxy) if proxy is not None else None,
        ) as response:
            yield AiohttpHttpResponse(self.aiohttp_session, response)

    @asynccontextmanager
    async def put(
        self,
        url: Union[str, URL],
        data: Union[str, bytes],
        headers: Dict[str, str] = None,
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        async with self.aiohttp_session.put(
            url,
            headers=headers,
            data=data,
            proxy=proxysetting_transform(proxy) if proxy is not None else None,
        ) as response:
            yield AiohttpHttpResponse(self.aiohttp_session, response)

    @asynccontextmanager
    async def delete(
        self,
        url: Union[str, URL],
        data: Union[str, bytes],
        headers: Dict[str, str] = None,
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        async with self.aiohttp_session.delete(
            url,
            headers=headers,
            data=data,
            proxy=proxysetting_transform(proxy) if proxy is not None else None,
        ) as response:
            yield AiohttpHttpResponse(self.aiohttp_session, response)

    @asynccontextmanager
    async def patch(
        self,
        url: Union[str, URL],
        data: Union[str, bytes],
        headers: Dict[str, str] = None,
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        async with self.aiohttp_session.patch(
            url,
            headers=headers,
            data=data,
            proxy=proxysetting_transform(proxy) if proxy is not None else None,
        ) as response:
            yield AiohttpHttpResponse(self.aiohttp_session, response)

    @asynccontextmanager
    async def websocket_connect(
        self,
        url: Union[str, URL],
        headers: Dict[str, str] = None,
        retries_count: int = 3,
    ) -> "AsyncGenerator[AiohttpWebsocketClientConnection, None]":
        origin_count = retries_count
        conn = AiohttpWebsocketClientConnection(self.aiohttp_session)
        yield conn
        logger.debug("websocket connection start")
        while retries_count > 0:
            try:
                async with self.aiohttp_session.ws_connect(
                    url,
                    headers=headers,
                ) as response:
                    conn.response = response
                    conn.ready.set()
                    for callback in conn.connected_callbacks:
                        await callback(conn)
                    async for message in response:
                        logger.debug(f"websocket message received: {message}")
                        if message.type == WSMsgType.TEXT:
                            await asyncio.gather(
                                *[
                                    callback(conn, Stream(message.data.encode()))
                                    for callback in conn.received_callbacks
                                ]
                            )
                        elif message.type == WSMsgType.BINARY:
                            await asyncio.gather(
                                *[
                                    callback(conn, Stream(message.data))
                                    for callback in conn.received_callbacks
                                ]
                            )
                        elif message.type == WSMsgType.PING:
                            await conn.pong()
                        elif message.type == WSMsgType.PONG:
                            pass
                        elif message.type == WSMsgType.CLOSE:
                            await asyncio.gather(*[callback(conn) for callback in conn.close_callbacks])
                        elif message.type == WSMsgType.CLOSED:
                            pass
                        elif message.type == WSMsgType.ERROR:
                            pass
                        else:
                            logger.warning(f"Unknown websocket message type: {message.type}")
            except Exception as e:
                logger.exception(
                    f"Websocket connection failed: {e}, for url: {url}, retries left: {retries_count}"
                )
                # try to retry
                await asyncio.gather(*[callback(conn, e) for callback in conn.error_callbacks])
                if retries_count > 0:
                    retries_count -= 1
                    # wait for a while, the retries greater, the wait shorter
                    await asyncio.sleep((origin_count - retries_count) * 5)


class AiohttpService(Service):
    supported_interface_types = {AiohttpClient, HttpClient, WebsocketClient}

    client_session: ClientSession

    def __init__(self, client_session: ClientSession = None) -> None:
        self.client_session = client_session or ClientSession()
        super().__init__()

    def get_interface(self, interface_type: Type[AiohttpClient]) -> AiohttpClient:
        if issubclass(interface_type, (HttpClient, WebsocketClient)):
            return AiohttpClient(self, self.client_session)
        raise ValueError(f"unsupported interface type {interface_type}")

    def get_status(self, entity: entity_selector = None):
        if entity is None:
            return self.status
        if entity not in self.status:
            raise KeyError(f"{entity} not in status")
        return self.status[entity]

    @property
    def launch_component(self) -> LaunchComponent:
        return LaunchComponent(
            "http.universal_client",
            set(),
            cleanup=lambda _: self.client_session.close(),
        )
