from __future__ import annotations

from pathlib import Path

from avilla.core.resource import Resource
from avilla.core.selector import Selector


class RedResource(Resource[bytes]):
    id: str
    size: int
    name: str
    elem: str
    uuid: str

    def __init__(self, selector: Selector, id: str, size: int, name: str, elem: str, uuid: str):
        super().__init__(selector)
        self.id = id
        self.size = size
        self.name = name
        self.elem = elem
        self.uuid = uuid


class RedFileResource(RedResource):
    pass


class RedImageResource(RedResource):
    def __init__(
        self,
        selector: Selector,
        id: str,
        size: int,
        name: str,
        elem: str,
        uuid: str,
        path: str | Path,
        width: int,
        height: int,
    ):
        super().__init__(selector, id, size, name, elem, uuid)
        self.path = Path(path)
        self.width = width
        self.height = height

    @property
    def url(self) -> str:
        return f"https://gchat.qpic.cn/gchatpic_new/0/0-0-{self.id.upper()}/0"


class RedVoiceResource(RedResource):
    def __init__(
        self,
        selector: Selector,
        id: str,
        size: int,
        name: str,
        elem: str,
        uuid: str,
        path: str | Path,
    ):
        super().__init__(selector, id, size, name, elem, uuid)
        self.path = Path(path)
