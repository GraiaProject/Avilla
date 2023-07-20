from __future__ import annotations

from pathlib import Path

from avilla.core.resource import Resource
from avilla.core.selector import Selector


class RedResource(Resource[bytes]):
    id: str
    name: str
    path: Path

    def __init__(self, selector: Selector, id: str, name: str, path: str | Path):
        super().__init__(selector)
        self.id = id
        self.name = name
        self.path = Path(path)


class RedImageResource(RedResource):
    pass


class RedVoiceResource(RedResource):
    pass
