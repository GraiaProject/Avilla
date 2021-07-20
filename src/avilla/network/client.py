"""services: Avilla as a Server
clients: Avilla as a Client
"""

import abc
from typing import Any, Dict, List, Union
from yarl import URL

from avilla.utilles.translator import OriginProvider


class Client:
    pass

class AbstractHttpClient(Client, abc.ABC):
    @abc.abstractmethod
    async def request(self, method: str, url: URL, *args, **kwargs) -> OriginProvider[bytes]: ...

    @abc.abstractmethod
    async def get(self, url: URL, *args, **kwargs) -> OriginProvider[bytes]: ...

    @abc.abstractmethod
    async def post(self, url: URL, data: bytes = None, json: Union[Dict[str], List] = None, *args, **kwargs) -> OriginProvider[bytes]: ...

    @abc.abstractmethod
    async def put(self, url: URL, *args, **kwargs) -> OriginProvider[bytes]: ...

    @abc.abstractmethod
    async def delete(self, url: URL, *args, **kwargs) -> OriginProvider[bytes]: ...

    @abc.abstractmethod
    async def patch(self, url: URL, *args, **kwargs) -> OriginProvider[bytes]: ...

class AbstractWebsocketClient(Client, abc.ABC):
    connections: Dict[str, Any]

    def __init__(self) -> None:
        self.connections = {}

    @abc.abstractmethod
    async def connect(self, url: URL, *args, **kwargs) -> str: ...

    @abc.abstractmethod
    async def close(self, connection_id: str, code: int) -> None: ...

    @abc.abstractmethod
    async def send(self, connection_id: str, data: bytes) -> None: ...

    @abc.abstractmethod
    async def send_text(self, connection_id: str, text: str) -> None: ...

    @abc.abstractmethod
    async def recv(self, connection_id: str) -> OriginProvider[bytes]: ...

    @abc.abstractmethod
    async def recv_text(self, connection_id: str) -> OriginProvider[str]: ...

    @abc.abstractmethod
    async def is_closed(self, connection_id: str) -> bool: ...