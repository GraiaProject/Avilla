from abc import ABCMeta, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Dict,
    List,
    Literal,
    MutableMapping,
    Optional,
    Type,
    Union,
)

from yarl import URL

from avilla.core.service import ExportInterface
from avilla.core.service.session import BehaviourSession
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
    protocol: Union[Literal["http"], Literal["https"], Literal["socks5"]]
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
        headers: Dict[str, str] = None,
        data: Union[str, bytes] = None,
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[HttpClientResponse, None]":
        ...

    @abstractmethod
    @asynccontextmanager
    def get(
        self,
        url: Union[str, URL],
        headers: Dict[str, str] = None,
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[HttpClientResponse, None]":
        ...

    @abstractmethod
    @asynccontextmanager
    def post(
        self,
        url: Union[str, URL],
        data: Union[str, bytes],
        headers: Dict[str, str] = None,
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[HttpClientResponse, None]":
        ...

    @abstractmethod
    @asynccontextmanager
    def put(
        self,
        url: Union[str, URL],
        data: Union[str, bytes],
        headers: Dict[str, str] = None,
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[HttpClientResponse, None]":
        ...

    @abstractmethod
    @asynccontextmanager
    def delete(
        self,
        url: Union[str, URL],
        headers: Dict[str, str] = None,
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[HttpClientResponse, None]":
        ...

    @abstractmethod
    @asynccontextmanager
    def patch(
        self,
        url: Union[str, URL],
        data: Union[str, bytes],
        headers: Dict[str, str] = None,
        proxy: ProxySetting = None,
    ) -> "AsyncGenerator[HttpClientResponse, None]":
        ...


class WebsocketClient(ExportInterface, metaclass=ABCMeta):
    @abstractmethod
    @asynccontextmanager
    def websocket_connect(
        self,
        url: Union[str, URL],
        headers: Dict[str, str] = None,
        retries_count: int = 3,
    ) -> "AsyncGenerator[WebsocketConnection, None]":
        ...


class HttpServer(ExportInterface, metaclass=ABCMeta):
    @abstractmethod
    def http_listen(
        self, path: str, methods: List[HTTP_METHODS] = None
    ) -> "Callable[[Callable[[HttpServerRequest], Any]], Any]":
        ...


class WebsocketServer(ExportInterface, metaclass=ABCMeta):
    @abstractmethod
    def websocket_listen(self, path: str) -> "Callable[[Callable[[WebsocketConnection], Any]], Any]":
        ...


class ASGIHandlerProvider(ExportInterface, metaclass=ABCMeta):
    @abstractmethod
    def get_asgi_handler(
        self,
    ) -> """Callable[[
        Type[MutableMapping[str, Any]],
        Awaitable[MutableMapping[str, Any]],
        Callable[[MutableMapping[str, Any]], Awaitable[None]]
    ], None]""":
        ...


class HttpPacketMixin:
    url: URL

    @abstractmethod
    async def read(self) -> Stream[bytes]:
        ...

    @abstractmethod
    async def cookies(self) -> Dict[str, str]:
        ...

    @abstractmethod
    async def headers(self) -> Dict[str, str]:
        ...


class HttpClientResponse(BehaviourSession, HttpPacketMixin, metaclass=ABCMeta):
    @abstractmethod
    async def close(self):
        ...

    @property
    @abstractmethod
    def status(self) -> int:
        ...

    @abstractmethod
    def raise_for_status(self):
        ...


class HttpServerRequest(BehaviourSession, HttpPacketMixin, metaclass=ABCMeta):
    @abstractmethod
    async def response(self, desc: Any):
        ...

    @property
    @abstractmethod
    def method(self) -> HTTP_METHODS:
        ...

    @property
    @abstractmethod
    def path(self) -> str:
        ...


class WebsocketConnection(BehaviourSession):
    server_mode: bool

    @abstractmethod
    async def accept(self) -> None:
        pass

    @abstractmethod
    async def send(self, data: Union[Stream[bytes], bytes]) -> None:
        ...

    @abstractmethod
    async def receive(self) -> Stream[bytes]:
        ...

    @abstractmethod
    async def ping(self) -> None:
        ...

    @abstractmethod
    async def pong(self) -> None:
        ...

    @abstractmethod
    async def close(self, code: int = 1000, message: bytes = b"") -> None:
        ...

    @abstractmethod
    def status(self) -> int:
        ...

    @abstractmethod
    def raise_for_code(self):
        ...

    @abstractmethod
    def on_received(self, callback: Callable[["WebsocketConnection", Stream[bytes]], Awaitable[Any]]):
        ...

    @abstractmethod
    def on_error(self, callback: Callable[["WebsocketConnection", Exception], Awaitable[Any]]):
        ...

    @abstractmethod
    def on_close(self, callback: Callable[["WebsocketConnection"], Awaitable[Any]]):
        ...
