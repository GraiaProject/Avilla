import asyncio
from contextlib import asynccontextmanager
from inspect import isclass
from typing import AsyncGenerator, Callable, Dict, Type, Union

import aiohttp
from aiohttp import ClientResponse, ClientSession
from aiohttp.client_ws import ClientWebSocketResponse
from aiohttp.helpers import BasicAuth, ProxyInfo
from loguru import logger
from yarl import URL

from avilla.core.launch import LaunchComponent
from avilla.core.selectors import entity as entity_selector
from avilla.core.service import Service
from avilla.core.service.common.http import (
    HTTP_METHODS,
    HttpClient,
    HttpClientResponse,
    ProxySetting,
    WebsocketClient,
)
from avilla.core.service.session import BehaviourSession
from avilla.core.stream import Stream


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

    def raise_for_status(self):
        self.response.raise_for_status()
    
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
        proxy: ProxySetting = None,
        retries_count: int = 3,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        async with self.aiohttp_session.ws_connect(url, headers=headers) as ws:
            yield AiohttpWebsocketSession(self.aiohttp_session, ws)
            # TODO


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
