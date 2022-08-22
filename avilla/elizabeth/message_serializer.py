from __future__ import annotations

import base64
from typing import TYPE_CHECKING

from graia.amnesia.message.element import Text

from avilla.core.context import ctx_relationship
from avilla.core.elements import Audio, Notice, NoticeAll, Picture
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

    @element(Picture)
    async def image(self, protocol: "ElizabethProtocol", element: Picture):
        raw = await ctx_relationship.get().fetch(element.resource)
        return {
            "type": "Image",
            "base64": base64.b64encode(raw).decode("utf-8"),
        }

    @element(FlashImage)
    async def flash_image(self, protocol: "ElizabethProtocol", element: FlashImage):
        raw = await ctx_relationship.get().fetch(element.resource)
        return {
            "type": "FlashImage",
            "base64": base64.b64encode(raw).decode("utf-8"),
        }

    @element(Audio)
    async def voice(self, protocol: "ElizabethProtocol", element: Audio):
        raw = await ctx_relationship.get().fetch(element.resource)
        return {"type": "Voice", "base64": base64.b64encode(raw).decode("utf-8")}
