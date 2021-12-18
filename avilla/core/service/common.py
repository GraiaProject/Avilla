from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, AsyncGenerator, Callable, Dict, Literal, Optional, Union

from yarl import URL

from avilla.core.service.entity import Activity, BehaviourDescription
from avilla.core.service import ExportInterface
from avilla.core.service.session import BehaviourSession
from contextlib import asynccontextmanager
from avilla.core.stream import Stream

HTTP_METHODS = Union[
    Literal["get"],
    Literal["post"],
    Literal["put"],
    Literal["delete"],
    Literal["patch"],
]


@dataclass
class ProxySetting:
    protocol: Union[Literal['http'], Literal['https'], Literal['socks5']]
    host: str
    port: int
    auth_username: Optional[str] = None
    auth_password: Optional[str] = None


class HttpClient(ExportInterface, metaclass=ABCMeta):
    base_url: URL

    @abstractmethod
    @asynccontextmanager
    def request(
        self,
        method: "HTTP_METHODS",
        url: Union[str, URL],
        headers: Dict[str, str],
        data: Union[str, bytes] = None,
        response_encoding: str = "utf-8",
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        ...

    @abstractmethod
    @asynccontextmanager
    def get(
        self,
        url: Union[str, URL],
        headers: Dict[str, str],
        response_encoding: str = "utf-8",
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        ...

    @abstractmethod
    @asynccontextmanager
    def post(
        self,
        url: Union[str, URL],
        headers: Dict[str, str],
        data: Union[str, bytes],
        response_encoding: str = "utf-8",
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        ...

    @abstractmethod
    @asynccontextmanager
    def put(
        self,
        url: Union[str, URL],
        headers: Dict[str, str],
        data: Union[str, bytes],
        response_encoding: str = "utf-8",
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        ...

    @abstractmethod
    @asynccontextmanager
    def delete(
        self,
        url: Union[str, URL],
        headers: Dict[str, str],
        response_encoding: str = "utf-8",
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        ...

    @abstractmethod
    @asynccontextmanager
    def patch(
        self,
        url: Union[str, URL],
        headers: Dict[str, str],
        data: Union[str, bytes],
        response_encoding: str = "utf-8",
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        ...


class WebsocketClient(ExportInterface, metaclass=ABCMeta):
    @abstractmethod
    @asynccontextmanager
    def websocket_connect(
        self,
        url: Union[str, URL],
        headers: Dict[str, str],
        proxy: ProxySetting = None,
        retries_count: int = 3,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        ...

# NOTE: 这里的 Websocket Client 实现需要实现自动重连(扩展行为 PostConnected, PostDisconnected, 并且要求上层, 也就是使用 Session 进行交互的一层, 更新 Status),
# 并且更新 BehaviourSession 中的 activity handlers.


@dataclass
class content_read(Activity[bytes]):
    length: Optional[int] = None


@dataclass
class content_write(Activity[None]):
    data: Union[str, bytes]


@dataclass
class httpstatus_get(Activity[int]):
    pass


@dataclass
class httpstatus_set(Activity[None]):
    status: int


@dataclass
class httpheader_get(Activity[str]):
    key: str


@dataclass
class httpheader_set(Activity[None]):
    key: str
    value: str


@dataclass
class httpcookie_get(Activity[str]):
    key: str


@dataclass
class httpcookie_set(Activity[None]):
    key: str
    value: str
    expire: Optional[timedelta] = None


@dataclass
class httpcookie_delete(Activity[None]):
    key: str


@dataclass
class PostConnected(BehaviourDescription[Callable[[ExportInterface, BehaviourSession, dict], Any]]):
    pass


@dataclass
class DataReceived(BehaviourDescription[Callable[[ExportInterface, BehaviourSession, dict, Stream[bytes]], Any]]):
    pass


@dataclass
class PostDisconnected(BehaviourDescription[Callable[[ExportInterface, BehaviourSession, dict], Any]]):
    pass
