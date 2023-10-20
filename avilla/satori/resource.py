from __future__ import annotations

from avilla.core.resource import Resource
from avilla.core.selector import Selector

from satori.element import Resource as RawResource

class SatoriResource(Resource[bytes], RawResource):
    def __init__(
        self,
        src: str,
        cache: bool | None = None,
        timeout:  str | None = None
    ):
        RawResource.__init__(self, src, cache, timeout)



class SatoriImageResource(SatoriResource):
    def __init__(
        self,
        src: str,
        cache: bool | None = None,
        timeout:  str | None = None,
        width: int | None = None,
        height: int | None = None
    ):
        super().__init__(src, cache, timeout)
        self.width = width
        self.height = height


class SatoriAudioResource(SatoriResource):
    pass


class SatoriVideoResource(SatoriResource):
    pass


class SatoriFileResource(SatoriResource):
    pass
