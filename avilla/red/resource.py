from __future__ import annotations

from pathlib import Path

from avilla.core.context import Context
from avilla.core.resource import Resource
from avilla.core.selector import Selector


class RedResource(Resource[bytes]):
    id: str
    ctx: Context
    size: int
    name: str
    elem: str
    uuid: str

    def __init__(self, ctx: Context, selector: Selector, id: str, size: int, name: str, elem: str, uuid: str):
        super().__init__(selector)
        self.ctx = ctx
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
        ctx: Context,
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
        super().__init__(ctx, selector, id, size, name, elem, uuid)
        self.path = Path(path)
        self.width = width
        self.height = height

    @property
    def url(self) -> str:
        if self.ctx.scene.last_key == "friend":
            return f"https://c2cpicdw.qpic.cn/offpic_new//{self.ctx.scene.last_value}-0-{self.id.upper()}/0"
        return f"https://gchat.qpic.cn/gchatpic_new/0/0-0-{self.id.upper()}/0"


class RedVoiceResource(RedResource):
    def __init__(
        self,
        ctx: Context,
        selector: Selector,
        id: str,
        size: int,
        name: str,
        elem: str,
        uuid: str,
        path: str | Path,
    ):
        super().__init__(ctx, selector, id, size, name, elem, uuid)
        self.path = Path(path)


class RedVideoResource(RedResource):
    def __init__(
        self,
        ctx: Context,
        selector: Selector,
        id: str,
        size: int,
        name: str,
        elem: str,
        uuid: str,
        path: str | Path,
    ):
        super().__init__(ctx, selector, id, size, name, elem, uuid)
        self.path = Path(path)
