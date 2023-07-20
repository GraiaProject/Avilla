from __future__ import annotations

from pathlib import Path

from avilla.core.resource import Resource
from avilla.core.selector import Selector


class RedResource(Resource[bytes]):
    id: str
    size: int
    name: str
    elem: str
    path: Path | None

    def __init__(self, selector: Selector, id: str, size: int, name: str, elem: str, path: str | Path | None = None):
        super().__init__(selector)
        self.id = id
        self.size = size
        self.name = name
        self.path = Path(path) if path else None


class RedImageResource(RedResource):
    def __init__(
        self,
        selector: Selector,
        id: str,
        size: int,
        name: str,
        elem: str,
        path: str | Path,
        width: int,
        height: int,
    ):
        super().__init__(selector, id, size, name, elem, path)
        self.width = width
        self.height = height


class RedVoiceResource(RedResource):
    pass
