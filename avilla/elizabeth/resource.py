from __future__ import annotations

from avilla.core.resource import Resource
from avilla.core.context import ContextSceneSelector
from avilla.core.selector import Selector


class ElizabethResource(Resource[bytes]):
    url: str | None = None
    path: str | None = None
    base64: str | None = None
    scene: ContextSceneSelector | None = None

    def __init__(
        self,
        id: str,
        url: str | None = None,
        path: str | None = None,
        base64: str | None = None,
        scene: ContextSceneSelector | None = None,
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
        return (self.scene.copy() if self.scene is not None else Selector()).appendix(self.type, self.id)


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
        scene: ContextSceneSelector | None = None,
    ) -> None:
        super().__init__(id, url, path, base64, scene)
        self.length = length

    @property
    def type(self) -> str:
        return "audio"
