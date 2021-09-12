"""services: Avilla as a Server
clients: Avilla as a Client
"""

import abc
import random
import string
from typing import Any, Callable, Dict, List, Union

from yarl import URL

from avilla.core.utilles.transformer import OriginProvider


class Client:
    pass


class AbstractHttpClient(Client, abc.ABC):
    @abc.abstractmethod
    async def request(self, method: str, url: URL, *args, **kwargs) -> OriginProvider[bytes]:
        ...

    @abc.abstractmethod
    async def get(self, url: URL, *args, **kwargs) -> OriginProvider[bytes]:
        ...

    @abc.abstractmethod
    async def post(
        self,
        url: URL,
        data: bytes = None,
        json: Union[Dict[str, Any], List] = None,
        *args,
        **kwargs,
    ) -> OriginProvider[bytes]:
        ...

    @abc.abstractmethod
    async def put(self, url: URL, *args, **kwargs) -> OriginProvider[bytes]:
        ...

    @abc.abstractmethod
    async def delete(self, url: URL, *args, **kwargs) -> OriginProvider[bytes]:
        ...

    @abc.abstractmethod
    async def patch(self, url: URL, *args, **kwargs) -> OriginProvider[bytes]:
        ...


WsConnectionCreatedCb = Callable[["AbstractWebsocketClient", str], Any]
WsDataReceivedCb = Callable[["AbstractWebsocketClient", str, Union[bytes, str]], Any]
WsConnectionClosedCb = Callable[["AbstractWebsocketClient", str], Any]


class AbstractWebsocketClient(Client, abc.ABC):
    connections: Dict[str, Any]

    cb_connection_created: Dict[str, List[WsConnectionCreatedCb]]
    cb_data_received: Dict[str, List[WsDataReceivedCb]]
    cb_connection_closed: Dict[str, List[WsConnectionClosedCb]]

    def __init__(self) -> None:
        self.connections = {}
        self.cb_connection_created = {}
        self.cb_data_received = {}
        self.cb_connection_closed = {}

    def on_created(self, connid: str):
        def wrapper(func: WsConnectionCreatedCb):
            self.cb_connection_created.setdefault(connid, []).append(func)
            return func

        return wrapper

    def on_received_data(self, connid: str):
        def wrapper(func: WsDataReceivedCb):
            self.cb_data_received.setdefault(connid, []).append(func)
            return func

        return wrapper

    def on_closed(self, connid: str):
        def wrapper(func: WsConnectionClosedCb):
            self.cb_connection_closed.setdefault(connid, []).append(func)
            return func

        return wrapper

    @staticmethod
    def gen_conn_id() -> str:
        return "".join(random.choices(string.ascii_letters + string.digits, k=12))

    @abc.abstractmethod
    async def connect(self, url: URL, *args, **kwargs) -> str:
        ...

    @abc.abstractmethod
    async def close(self, connection_id: str, code: int) -> None:
        ...

    @abc.abstractmethod
    async def send(self, connection_id: str, data: bytes) -> None:
        ...

    @abc.abstractmethod
    async def send_text(self, connection_id: str, text: str) -> None:
        ...

    @abc.abstractmethod
    async def send_json(self, connection_id: str, data: Dict[str, Any]) -> None:
        ...

    @abc.abstractmethod
    async def is_closed(self, connection_id: str) -> bool:
        ...
