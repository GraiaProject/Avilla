import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable, Dict, Type, Union

import aiohttp
from aiohttp import ClientSession
from aiohttp.client_ws import ClientWebSocketResponse
from aiohttp.helpers import BasicAuth, ProxyInfo
from loguru import logger
from yarl import URL

from avilla.core.service.common import (
    HTTP_METHODS,
    HttpClient,
    ProxySetting,
    WebsocketClient,
)
from avilla.core.service.entity import BehaviourDescription
from avilla.core.stream import Stream

from .common import (
    DataReceived,
    PostConnected,
    PostDisconnected,
    content_read,
    content_write,
    httpcookie_delete,
    httpcookie_get,
    httpcookie_set,
    httpheader_get,
    httpheader_set,
    httpstatus_get,
    httpstatus_set,
)
from .session import BehaviourSession


def proxysetting_transform(proxy_setting: ProxySetting) -> ProxyInfo:
    return ProxyInfo(
        URL(f"{proxy_setting.protocol}://{proxy_setting.host}:{proxy_setting.port}"),
        BasicAuth(proxy_setting.auth_username, proxy_setting.auth_password)
        if proxy_setting.auth_username and proxy_setting.auth_password
        else None,
    )


class AiohttpClient(HttpClient, WebsocketClient):
    aiohttp_session: ClientSession

    def __init__(self, aiohttp_session: ClientSession) -> None:
        self.aiohttp_session = aiohttp_session
        super().__init__()

    @asynccontextmanager
    async def request(
        self,
        method: "HTTP_METHODS",
        url: Union[str, URL],
        headers: Dict[str, str],
        data: Union[str, bytes] = None,
        response_encoding: str = "utf-8",
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        async with self.aiohttp_session.request(
            method,
            url,
            headers=headers,
            data=data,
            proxy=proxysetting_transform(proxy) if proxy is not None else None,
        ) as response:

            async def content_reader(_) -> bytes:
                return await response.read()

            yield BehaviourSession(
                self.service,
                self,
                {
                    content_read: content_reader,
                    httpstatus_get: lambda _: response.status,
                    httpcookie_get: lambda _: response.cookies,
                    httpheader_get: lambda _: response.headers,
                },
            )

    @asynccontextmanager
    async def get(
        self,
        url: Union[str, URL],
        headers: Dict[str, str],
        response_encoding: str = "utf-8",
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        async with self.aiohttp_session.get(
            url, headers=headers, proxy=proxysetting_transform(proxy) if proxy is not None else None
        ) as response:

            async def content_reader(_) -> bytes:
                return await response.read()

            yield BehaviourSession(
                self.service,
                self,
                {
                    content_read: content_reader,
                    httpstatus_get: lambda _: response.status,
                    httpcookie_get: lambda _: response.cookies,
                    httpheader_get: lambda _: response.headers,
                },
            )

    @asynccontextmanager
    async def post(
        self,
        url: Union[str, URL],
        headers: Dict[str, str],
        data: Union[str, bytes],
        response_encoding: str = "utf-8",
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        async with self.aiohttp_session.post(
            url,
            headers=headers,
            data=data,
            proxy=proxysetting_transform(proxy) if proxy is not None else None,
        ) as response:

            async def content_reader(_) -> bytes:
                return await response.read()

            yield BehaviourSession(
                self.service,
                self,
                {
                    content_read: content_reader,
                    httpstatus_get: lambda _: response.status,
                    httpcookie_get: lambda _: response.cookies,
                    httpheader_get: lambda _: response.headers,
                },
            )

    @asynccontextmanager
    async def put(
        self,
        url: Union[str, URL],
        headers: Dict[str, str],
        data: Union[str, bytes],
        response_encoding: str = "utf-8",
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        async with self.aiohttp_session.put(
            url,
            headers=headers,
            data=data,
            proxy=proxysetting_transform(proxy) if proxy is not None else None,
        ) as response:

            async def content_reader(_) -> bytes:
                return await response.read()

            yield BehaviourSession(
                self.service,
                self,
                {
                    content_read: content_reader,
                    httpstatus_get: lambda _: response.status,
                    httpcookie_get: lambda _: response.cookies,
                    httpheader_get: lambda _: response.headers,
                },
            )

    @asynccontextmanager
    async def delete(
        self,
        url: Union[str, URL],
        headers: Dict[str, str],
        data: Union[str, bytes],
        response_encoding: str = "utf-8",
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        async with self.aiohttp_session.delete(
            url,
            headers=headers,
            data=data,
            proxy=proxysetting_transform(proxy) if proxy is not None else None,
        ) as response:

            async def content_reader(_) -> bytes:
                return await response.read()

            yield BehaviourSession(
                self.service,
                self,
                {
                    content_read: content_reader,
                    httpstatus_get: lambda _: response.status,
                    httpcookie_get: lambda _: response.cookies,
                    httpheader_get: lambda _: response.headers,
                },
            )

    @asynccontextmanager
    async def patch(
        self,
        url: Union[str, URL],
        headers: Dict[str, str],
        data: Union[str, bytes],
        response_encoding: str = "utf-8",
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        async with self.aiohttp_session.patch(
            url,
            headers=headers,
            data=data,
            proxy=proxysetting_transform(proxy) if proxy is not None else None,
        ) as response:

            async def content_reader(_) -> bytes:
                return await response.read()

            yield BehaviourSession(
                self.service,
                self,
                {
                    content_read: content_reader,
                    httpstatus_get: lambda _: response.status,
                    httpcookie_get: lambda _: response.cookies,
                    httpheader_get: lambda _: response.headers,
                },
            )

    @asynccontextmanager
    async def websocket_connect(
        self,
        url: Union[str, URL],
        headers: Dict[str, str],
        proxy: ProxySetting = None,
        retries_count: int = 3,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        cbs = {
            PostConnected: [],
            DataReceived: [],
            PostDisconnected: [],
        }

        def cb_handler(
            behaviour: Union[Type[BehaviourDescription], BehaviourDescription], callback: Callable
        ) -> None:
            if behaviour is DataReceived or isinstance(behaviour, DataReceived):
                cbs[DataReceived].append(callback)
            elif behaviour is PostConnected or isinstance(behaviour, PostConnected):
                cbs[PostConnected].append(callback)
            elif behaviour is PostDisconnected or isinstance(behaviour, PostDisconnected):
                cbs[PostDisconnected].append(callback)

        prepared_signal = asyncio.Event()
        behaviour_session = BehaviourSession(self.service, self, {}, cb_handler, prepared_signal)
        # 这里的 Activity Handlers 会在连接建立成功后才会更新上去
        while retries_count > 0:
            try:
                async with self.aiohttp_session.ws_connect(url, headers=headers) as ws_session:

                    async def handle_task(ws_session: ClientWebSocketResponse):
                        await prepared_signal.wait()
                        behaviour_session.update_activity_handlers(
                            {
                                # todo: 主动操作
                            }
                        )
                        current_session_stats = {}
                        await asyncio.gather(
                            cb(self, behaviour_session, current_session_stats) for cb in cbs[PostConnected]
                        )
                        async for message in ws_session:
                            if message.type == aiohttp.WSMsgType.TEXT:
                                await asyncio.gather(
                                    cb(
                                        self,
                                        behaviour_session,
                                        current_session_stats,
                                        Stream(message.data.encode()),
                                    )
                                    for cb in cbs[DataReceived]
                                )
                            elif message.type == aiohttp.WSMsgType.BINARY:
                                await asyncio.gather(
                                    cb(self, behaviour_session, current_session_stats, Stream(message.data))
                                    for cb in cbs[DataReceived]
                                )
                            elif message.type == aiohttp.WSMsgType.CLOSED:
                                logger.warning(f"webSocket connection on {url} closed")
                                await asyncio.gather(
                                    cb(self, behaviour_session, current_session_stats)
                                    for cb in cbs[PostDisconnected]
                                )
                                break

                    asyncio.get_running_loop().create_task(handle_task(ws_session))
                    yield behaviour_session
                break
            except Exception as e:
                retries_count -= 1
                if retries_count == 0:
                    raise e
                else:
                    logger.exception(e)
                logger.warning(f"retrying websocket connection to {url} after 10 seconds")
                await asyncio.sleep(10)
