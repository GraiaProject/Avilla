from dataclasses import dataclass
from typing import Dict, TypeVar, Union

from yarl import URL


@dataclass
class HttpClientInfo:
    account: int
    verify_key: str
    host: str

    def get_url(self, route: str) -> str:
        return str((URL(self.host) / route))

@dataclass
class WebsocketClientInfo:
    account: int
    verify_key: str
    host: str

    def get_url(self, route: str) -> str:
        return str((URL(self.host) / route))

@dataclass
class WebsocketServerInfo:
    account: int
    verify_key: str
    path: str
    params: Dict[str, str]
    headers: Dict[str, str]

@dataclass
class HttpServerInfo:
    account: int
    path: str
    headers: Dict[str, str]


U_Info = Union[HttpClientInfo, WebsocketClientInfo, WebsocketServerInfo, HttpServerInfo]

T_Info = TypeVar("T_Info", bound=U_Info)
