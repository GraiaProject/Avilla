from __future__ import annotations

from typing import TYPE_CHECKING

from graia.amnesia.message.element import Text

from avilla.core.elements import Audio, Notice, NoticeAll, Picture

from .resource import ElizabethAudioResource, ElizabethImageResource
from .util import element

if TYPE_CHECKING:
    from avilla.core.context import Context


@element("Plain")
async def plain(context: Context, raw: dict):
    return Text(raw["text"])


@element("At")
async def at(context: Context, raw: dict):
    if not context.scene.follows("group"):
        raise ValueError(f"At(Notice) element expected used in group scene, which currently {context.scene}")
    return Notice(context.scene.member(raw["target"]))


@element("AtAll")
async def at_all(context: Context, raw: dict):
    return NoticeAll()


@element("Image")
async def image(context: Context, raw: dict):
    return Picture(ElizabethImageResource(raw["imageId"], raw["url"], raw["path"], raw["base64"], context.scene))


@element("Voice")
async def voice(context: Context, raw: dict):
    return Audio(
        ElizabethAudioResource(raw["voiceId"], raw["url"], raw["path"], raw["base64"], raw["length"], context.scene)
    )
