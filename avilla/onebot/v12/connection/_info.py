from dataclasses import dataclass
from typing import TypeVar

from yarl import URL


class Info:
    access_token: str


ServerInfo = Info


@dataclass
class ClientInfo(Info):
    host: str
    access_token: str

    def get_url(self, route: str) -> str:
        return str((URL(self.host) / route))


T_Info = TypeVar("T_Info", bound=Info)
