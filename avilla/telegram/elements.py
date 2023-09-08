from pathlib import Path
from typing import IO

from telegram import InputFile, PhotoSize, Update
from telegram.constants import MessageType
from typing_extensions import Self


class MessageFragment:
    type: MessageType
    data: dict
    update: Update | None

    def __init__(self, _type: MessageType, data: dict, update: Update | None = None):
        self.type = _type
        self.data = data
        self.update = update

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def send(self):
        ...

    @classmethod
    def compose(cls, *fragments: Self):
        composed = []
        for fragment in fragments:
            if isinstance(fragment, MessageFragmentPhoto):
                composed.append(fragment)
            elif isinstance(fragment, MessageFragmentText):
                if not composed:
                    composed.append(fragment)
                elif composed[-1].type == MessageType.TEXT:
                    composed[-1].text += fragment.text
                elif composed[-1].type == MessageType.PHOTO:
                    composed[-1].caption = composed[-1].caption or "" + fragment.text
        return composed

    @classmethod
    def decompose(cls, update: Update) -> list[Self]:
        fragments = []
        if update.message.text:
            fragments.append(MessageFragmentText(update.message.text, update=update))
        if update.message.photo:
            if update.message.caption:
                fragments.append(MessageFragmentPhoto(update.message.photo[-1], update=update))
                fragments.append(MessageFragmentText(update.message.caption, update=update))
            else:
                fragments.append(MessageFragmentPhoto(update.message.photo[-1], update=update))
        return fragments


class MessageFragmentText(MessageFragment):
    text: str

    def __init__(self, text: str, update: Update | None = None):
        super().__init__(MessageType.TEXT, {"text": text}, update)
        self.text = text


class MessageFragmentPhoto(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes | PhotoSize
    caption: str | None

    def __init__(
        self,
        file: str | Path | IO[bytes] | InputFile | bytes | PhotoSize,
        caption: str = None,
        update: Update | None = None,
    ):
        super().__init__(MessageType.PHOTO, {"file": file}, update)
        self.file = file
        self.caption = caption
