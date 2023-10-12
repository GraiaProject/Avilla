from __future__ import annotations

from avilla.core.resource import Resource
from avilla.core.selector import Selector


class SatoriResource(Resource[bytes]):
    src: str

    def __init__(self, selector: Selector, src: str, cache: bool = False):
        super().__init__(selector)
        self.src = src
        self.cache = cache


class SatoriImageResource(SatoriResource):
    def __init__(
            self,
            selector: Selector,
            src: str,
            width: int | None = None,
            height: int | None = None,
            cache: bool = False
    ):
        super().__init__(selector, src, cache)
        self.width = width
        self.height = height


class SatoriAudioResource(SatoriResource):
    pass


class SatoriVideoResource(SatoriResource):
    pass


class SatoriFileResource(SatoriResource):
    pass
