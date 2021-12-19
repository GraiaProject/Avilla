import asyncio
from contextlib import asynccontextmanager
from functools import partial
from inspect import isclass
from typing import AsyncGenerator, Callable, Dict, Type, Union

import aiohttp
from aiohttp import ClientSession
from aiohttp.client_ws import ClientWebSocketResponse
from aiohttp.helpers import BasicAuth, ProxyInfo
from loguru import logger
from yarl import URL

from avilla.core.launch import LaunchComponent
from avilla.core.selectors import entity as entity_selector
from avilla.core.service import Service
from avilla.core.service.common import (
    HTTP_METHODS,
    HttpClient,
    ProxySetting,
    WebsocketClient,
)
from avilla.core.service.entity import BehaviourDescription
from avilla.core.stream import Stream

from .common import (  # todo: 剩下还有一大堆操作.
    DataReceived,
    PostConnected,
    PostDisconnected,
    content_read,
    disconnect,
    httpcookie_get,
    httpheader_get,
    httpstatus_get,
    send_netmsg,
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
        headers: Dict[str, str] = None,
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
        data: Union[str, bytes],
        headers: Dict[str, str] = None,
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
        data: Union[str, bytes],
        headers: Dict[str, str] = None,
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
        data: Union[str, bytes],
        headers: Dict[str, str] = None,
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
        data: Union[str, bytes],
        headers: Dict[str, str] = None,
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
        headers: Dict[str, str] = None,
        proxy: ProxySetting = None,
        retries_count: int = 3,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        count_setting = retries_count
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

        def recount():
            nonlocal retries_count
            retries_count = count_setting
            logger.debug(f"retries count was reset to {retries_count}.")

        prepared_signal = asyncio.Event()
        behaviour_session = BehaviourSession(self.service, self, {}, prepared_signal)
        recover_retrites_task = None
        while retries_count > 0:
            try:
                async with self.aiohttp_session.ws_connect(url, headers=headers) as ws_session:

                    async def netmsg_sender(activity: Union[send_netmsg, Type[send_netmsg]]):
                        if isclass(activity):
                            raise TypeError("this activity must be an instance")
                        if isinstance(activity.data, str):
                            await ws_session.send_str(activity.data)
                        elif isinstance(activity.data, bytes):
                            await ws_session.send_bytes(activity.data)
                        else:
                            raise ValueError(f"Unsupported data type: {type(activity.data)}")

                    async def handle_task(ws_session: ClientWebSocketResponse):
                        await prepared_signal.wait()
                        behaviour_session.update_activity_handlers(
                            {
                                send_netmsg: netmsg_sender,  # type: ignore
                                disconnect: lambda _: ws_session.close(),
                            }
                        )
                        behaviour_session.submit_behaviour_expansion(cb_handler)
                        current_session_stats = {}
                        await asyncio.gather(
                            *[cb(self, behaviour_session, current_session_stats) for cb in cbs[PostConnected]]
                        )
                        async for message in ws_session:
                            if message.type == aiohttp.WSMsgType.TEXT:
                                await asyncio.gather(
                                    *[
                                        cb(
                                            self,
                                            behaviour_session,
                                            current_session_stats,
                                            Stream(message.data.encode()),
                                        )
                                        for cb in cbs[DataReceived]
                                    ]
                                )
                            elif message.type == aiohttp.WSMsgType.BINARY:
                                await asyncio.gather(
                                    *[
                                        cb(
                                            self,
                                            behaviour_session,
                                            current_session_stats,
                                            Stream(message.data),
                                        )
                                        for cb in cbs[DataReceived]
                                    ]
                                )
                            elif message.type == aiohttp.WSMsgType.CLOSED:
                                logger.warning(f"webSocket connection on {url} closed")
                                await asyncio.gather(
                                    *[
                                        cb(self, behaviour_session, current_session_stats)
                                        for cb in cbs[PostDisconnected]
                                    ]
                                )
                                break

                    asyncio.get_running_loop().create_task(handle_task(ws_session))
                    yield behaviour_session
                break
            except Exception as e:
                if recover_retrites_task is not None:
                    recover_retrites_task.cancel()
                retries_count -= 1
                if retries_count == 0:
                    raise e
                else:
                    logger.exception(e)
                logger.warning(f"retrying websocket connection to {url} after 10 seconds")
                await asyncio.sleep(10)
                recover_retrites_task = asyncio.get_running_loop().call_later(30.0, recount)


class AiohttpService(Service):
    supported_interface_types = {AiohttpClient, HttpClient, WebsocketClient}
    supported_description_types = {DataReceived, PostConnected, PostDisconnected}

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

    async def launch_mainline(self):
        ...

    @property
    def launch_component(self) -> LaunchComponent:
        return LaunchComponent(
            "http.universal_client",
            set(),
            self.launch_mainline,
            self.client_session.__aenter__,
            partial(self.client_session.__aexit__, None, None, None),
        )
