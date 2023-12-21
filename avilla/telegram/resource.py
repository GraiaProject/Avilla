from __future__ import annotations

from telegram import (
    Animation,
    Audio,
    Document,
    File,
    PhotoSize,
    Sticker,
    Video,
    VideoNote,
    Voice,
)

from avilla.core.resource import Resource
from avilla.core.selector import Selector


class TelegramResource(Resource[bytes]):
    file: File
    media: Animation | Audio | Document | PhotoSize | Sticker | Video | VideoNote | Voice
    thumb: tuple[PhotoSize, ...] | None

    def __init__(
        self,
        selector: Selector,
        file: File,
        media: Animation | Audio | Document | PhotoSize | Sticker | Video | VideoNote | Voice,
        thumb: tuple[PhotoSize, ...] | None = None,
    ):
        super().__init__(selector)
        self.file = file
        self.media = media
        self.thumb = thumb
