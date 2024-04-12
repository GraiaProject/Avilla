from __future__ import annotations

from avilla.core.resource import Resource
from avilla.core.selector import Selector


class ElizabethResource(Resource[bytes]):
    id: str
    url: str | None

    def __init__(self, selector: Selector, id: str, url: str | None = None):
        super().__init__(selector)
        self.id = id
        self.url = url


class ElizabethImageResource(ElizabethResource):
    pass


class ElizabethVoiceResource(ElizabethResource):
    pass


class ElizabethVideoResource(ElizabethResource):
    pass


class ElizabethFileResource(ElizabethResource):
    name: str
    size: int

    def __init__(self, selector: Selector, id: str, url: str | None, name: str, size: int):
        super().__init__(selector, id, url)
        self.name = name
        self.size = size
