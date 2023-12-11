from __future__ import annotations

from telegram import Audio, Document, File, PhotoSize, Video

from avilla.core.resource import Resource
from avilla.core.selector import Selector


class TelegramResource(Resource[bytes]):
    file: File

    def __init__(self, selector: Selector, file: File):
        super().__init__(selector)
        self.file = file


class TelegramPhotoResource(TelegramResource):
    photo: tuple[PhotoSize, ...]

    def __init__(self, selector: Selector, file: File, photo: tuple[PhotoSize, ...]):
        super().__init__(selector, file)
        self.photo = photo

    @property
    def original(self):
        return self.photo[-1]


class TelegramThumbedResource(TelegramResource):
    media: Audio | Video | Document
    photo: tuple[PhotoSize, ...] | None

    def __init__(
        self, selector: Selector, file: File, media: Audio | Video | Document, photo: tuple[PhotoSize, ...] = None
    ):
        super().__init__(selector, file)
        self.media = media
        self.photo = photo
