from dataclasses import dataclass
from datetime import timedelta
from typing import Optional, Union

from avilla.core.service.entity import Activity


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
class send_netmsg(Activity[None]):
    data: Union[str, bytes]


@dataclass
class disconnect(Activity[None]):
    pass
