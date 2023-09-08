from __future__ import annotations

from telegram import File, PhotoSize

from avilla.core.resource import Resource
from avilla.core.selector import Selector


class TelegramResource(Resource[bytes]):
    file: File

    def __init__(self, selector: Selector, file: File):
        super().__init__(selector)
        self.file = file


class TelegramPhotoResource(TelegramResource):
    photo: tuple[PhotoSize]

    def __init__(self, selector: Selector, file: File, photo: tuple[PhotoSize]):
        super().__init__(selector, file)
        self.photo = photo

    @property
    def original(self):
        return self.photo[-1]


class TelegramRecordResource(TelegramResource):
    pass


class TelegramVideoResource(TelegramResource):
    pass


class TelegramFileResource(TelegramResource):
    pass
