from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Optional, Union

from avilla.core.service.entity import Activity
from avilla.core.stream import Stream


@dataclass
class content_read(Activity[Stream[bytes]]):
    length: Optional[int] = None


@dataclass
class content_write(Activity[None]):
    data: Union[str, bytes]


@dataclass
class get_status(Activity[int]):
    pass


@dataclass
class set_status(Activity[None]):
    status: int


@dataclass
class get_header(Activity[str]):
    key: str


@dataclass
class set_header(Activity[None]):
    key: str
    value: str


@dataclass
class get_cookie(Activity[str]):
    key: str


@dataclass
class set_cookie(Activity[None]):
    key: str
    value: str
    expire: Optional[timedelta] = None


@dataclass
class del_cookie(Activity[None]):
    key: str


@dataclass
class send(Activity[None]):
    data: Any


@dataclass
class respond(Activity[None]):
    data: Any


@dataclass
class disconnect(Activity[None]):
    pass


@dataclass
class accept(Activity[None]):
    pass
