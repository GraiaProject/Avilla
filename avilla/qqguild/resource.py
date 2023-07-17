from __future__ import annotations

from avilla.core.resource import Resource
from avilla.core.selector import Selector


class QQGuildResource(Resource[bytes]):
    id: str
    url: str | None

    def __init__(self, selector: Selector, id: str, url: str | None = None):
        super().__init__(selector)
        self.id = id
        self.url = url


class QQGuildImageResource(QQGuildResource):
    pass


class QQGuildVoiceResource(QQGuildResource):
    length: int | None

    def __init__(self, selector: Selector, id: str, url: str | None = None, length: int | None = None):
        super().__init__(selector, id, url)
        self.length = length


class QQGuildFileResource(QQGuildResource):
    name: str
    size: int

    def __init__(self, selector: Selector, id: str, url: str | None, name: str, size: int):
        super().__init__(selector, id, url)
        self.name = name
        self.size = size
