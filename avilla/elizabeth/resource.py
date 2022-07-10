from __future__ import annotations

from typing import TYPE_CHECKING

from graia.amnesia.builtins.aiohttp import AiohttpClientInterface
from launart import Launart

from avilla.core.resource import Resource, ResourceProvider
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from avilla.core.relationship import Relationship


class LaunartHttpResourceProvider(ResourceProvider):
    def __init__(self, launart: Launart):
        self.client = launart.get_interface(AiohttpClientInterface)

    async def fetch(self, resource: ElizabethResource, relationship: Relationship | None = None):
        if resource.url is None:
            raise ValueError("required url")
        return await self.client.request("GET", resource.url).io().read()

    def get_metadata_source(self):
        raise NotImplementedError()


class ElizabethResource(Resource[bytes]):
    url: str | None = None
    path: str | None = None
    base64: str | None = None

    def __init__(
        self,
        id: str,
        url: str | None = None,
        path: str | None = None,
        base64: str | None = None,
        mainline: Selector | None = None,
    ) -> None:
        self.id = id
        self.url = url
        self.path = path
        self.base64 = base64
        self.mainline = mainline

    def get_default_provider(self):
        return LaunartHttpResourceProvider(Launart.current())


class ElizabethImageResource(ElizabethResource):
    @property
    def resource_type(self) -> str | None:
        if self.mainline is not None:
            if self.mainline.path == "land.group":
                return "group_image"
            elif self.mainline.path == "land.friend":
                return "friend_image"
        return "image"


class ElizabethAudioResource(ElizabethResource):
    length: int | None = None

    def __init__(
        self,
        id: str,
        url: str | None = None,
        path: str | None = None,
        base64: str | None = None,
        mainline: Selector | None = None,
        length: int | None = None,
    ) -> None:
        super().__init__(id, url, path, base64, mainline)
        self.length = length

    @property
    def resource_type(self) -> str | None:
        return "audio"
