from __future__ import annotations

from avilla.core.resource import Resource
from avilla.core.selector import Selector


class ElizabethResource(Resource[bytes]):
    url: str | None = None
    path: str | None = None
    base64: str | None = None
    scene: Selector | None = None

    def __init__(
        self,
        id: str,
        url: str | None = None,
        path: str | None = None,
        base64: str | None = None,
        scene: Selector | None = None,
    ) -> None:
        self.id = id
        self.url = url
        self.path = path
        self.base64 = base64
        self.scene = scene

    @property
    def type(self) -> str:
        return "elizabeth_resource"

    @property
    def selector(self) -> Selector:
        return (self.scene or Selector()).appendix(self.type, self.id)


class ElizabethImageResource(ElizabethResource):
    @property
    def type(self) -> str:
        return "picture"


class ElizabethAudioResource(ElizabethResource):
    length: int | None = None

    def __init__(
        self,
        id: str,
        url: str | None = None,
        path: str | None = None,
        base64: str | None = None,
        length: int | None = None,
        scene: Selector | None = None,
    ) -> None:
        super().__init__(id, url, path, base64, scene)
        self.length = length

    @property
    def type(self) -> str:
        return "audio"
