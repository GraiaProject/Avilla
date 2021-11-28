from dataclasses import dataclass

from avilla.core.network.activity import Activity


@dataclass
class Write(Activity):
    content: bytes


@dataclass
class SetHeader(Activity):
    header: str
    value: str


@dataclass
class SetCookie(Activity):
    key: str
    value: str


@dataclass
class SetStatusCode(Activity):
    status: int
