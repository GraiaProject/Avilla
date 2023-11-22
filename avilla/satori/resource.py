from __future__ import annotations

from typing import Any

from satori.element import Resource as RawResource

from avilla.core.resource import Resource


class SatoriResource(Resource[bytes], RawResource):
    def __init__(self, src: str, extra: dict[str, Any] | None = None, cache: bool | None = None, timeout: str | None = None):
        RawResource.__init__(self, src, extra, cache, timeout)


class SatoriImageResource(SatoriResource):
    def __init__(
        self,
        src: str,
        extra: dict[str, Any] | None = None,
        cache: bool | None = None,
        timeout: str | None = None,
        width: int | None = None,
        height: int | None = None,
    ):
        super().__init__(src, extra, cache, timeout)
        self.width = width
        self.height = height


class SatoriAudioResource(SatoriResource):
    pass


class SatoriVideoResource(SatoriResource):
    pass


class SatoriFileResource(SatoriResource):
    pass
