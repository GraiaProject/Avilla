from __future__ import annotations

import base64
from typing import TYPE_CHECKING

from graia.amnesia.message.element import Text

from avilla.core.context import ctx_relationship
from avilla.core.elements import Audio, Image, Notice, NoticeAll
from avilla.core.resource import get_provider
from avilla.core.utilles.message_serializer import MessageSerializer, element
from avilla.elizabeth.element import FlashImage

if TYPE_CHECKING:
    from .protocol import ElizabethProtocol


class ElizabethMessageSerializer(MessageSerializer["ElizabethProtocol"]):
    @element(Text)
    def plain(self, protocol: "ElizabethProtocol", element: Text):
        return {"type": "Plain", "text": element.text}

    @element(Notice)
    def at(self, protocol: "ElizabethProtocol", element: Notice):
        return {"type": "At", "target": element.target.id}

    @element(NoticeAll)
    def at_all(self, protocol: "ElizabethProtocol", element: NoticeAll):
        return {"type": "AtAll"}

    @element(Image)
    async def image(self, protocol: "ElizabethProtocol", element: Image):
        provider = get_provider(element.resource, protocol=protocol)
        if provider is None:
            raise ValueError(f"No provider found for resource: {element.resource}")
        raw = await provider.fetch(element.resource, ctx_relationship.get())
        return {
            "type": "Image",
            "base64": base64.b64encode(raw).decode("utf-8"),
        }

    @element(FlashImage)
    async def flash_image(self, protocol: "ElizabethProtocol", element: FlashImage):
        provider = get_provider(element.resource, protocol=protocol)
        if provider is None:
            raise ValueError(f"No provider found for resource: {element.resource}")
        raw = await provider.fetch(element.resource, ctx_relationship.get())
        return {
            "type": "FlashImage",
            "base64": base64.b64encode(raw).decode("utf-8"),
        }

    @element(Audio)
    async def voice(self, protocol: "ElizabethProtocol", element: Audio):
        provider = get_provider(element.resource, protocol=protocol)
        if provider is None:
            raise ValueError(f"No provider found for resource: {element.resource}")
        raw = await provider.fetch(element.resource, ctx_relationship.get())
        return {"type": "Voice", "base64": base64.b64encode(raw).decode("utf-8")}
