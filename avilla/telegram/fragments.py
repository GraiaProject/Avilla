from pathlib import Path
from typing import IO

from telegram import (
    InputFile,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
    PhotoSize,
    Update,
)
from telegram.constants import MessageType
from telegram.ext import ExtBot
from typing_extensions import Self

from avilla.standard.telegram.elements import Contact

_MISSING = type("_MISSING", (), {})  # Used for elements that are not in MessageType but in API


class MessageFragment:
    type: MessageType
    update: Update | None

    def __init__(self, msg_type: MessageType | _MISSING, update: Update | None = None):
        self.type = msg_type
        self.update = update

    def __getitem__(self, item):
        return self.__getattribute__(item)

    async def send(self, bot: ExtBot, chat: int, /, reply_to: int = None) -> Message:
        ...

    @classmethod
    def sort(cls, *fragments: Self):
        return sorted(fragments, key=lambda f: PRIORITIES[f.__class__])

    @classmethod
    def compose(cls, *fragments: Self) -> list[Self]:
        composed = []
        for fragment in fragments:
            if not composed:
                composed.append(fragment)
            elif isinstance(
                fragment, (MessageFragmentPhoto, MessageFragmentAudio, MessageFragmentDocument, MessageFragmentVideo)
            ):
                if isinstance(composed[-1], (MessageFragmentPhoto, MessageFragmentAudio, MessageFragmentDocument)):
                    composed.append(MessageFragmentMediaGroup([composed.pop(), fragment]))
                elif isinstance(composed[-1], MessageFragmentMediaGroup):
                    if len(composed[-1].media) < 9:
                        composed[-1].media.append(fragment)
                    else:
                        composed.append(MessageFragmentMediaGroup([fragment]))
            elif isinstance(fragment, MessageFragmentText):
                if composed[-1].type == MessageType.TEXT:
                    composed[-1].text += fragment.text
                elif isinstance(
                    composed[-1],
                    (
                        MessageFragmentPhoto,
                        MessageFragmentAudio,
                        MessageFragmentDocument,
                        MessageFragmentVideo,
                        MessageFragmentMediaGroup,
                    ),
                ):
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
        super().__init__(MessageType.TEXT, update)
        self.text = text

    async def send(self, bot: ExtBot, chat: int, /, reply_to: int = None) -> Message:
        return await bot.send_message(chat, text=self.text)


class MessageFragmentPhoto(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes | PhotoSize
    caption: str | None

    def __init__(
        self,
        file: str | Path | IO[bytes] | InputFile | bytes | PhotoSize,
        caption: str = None,
        update: Update | None = None,
    ):
        super().__init__(MessageType.PHOTO, update)
        self.file = file
        self.caption = caption

    async def send(self, bot: ExtBot, chat: int, /, reply_to: int = None) -> Message:
        return await bot.send_photo(chat, photo=self.file, caption=self.caption)


class MessageFragmentAnimation(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes

    def __init__(self, file: str | Path | IO[bytes] | InputFile | bytes, update: Update | None = None):
        super().__init__(MessageType.ANIMATION, update)
        self.file = file

    async def send(self, bot: ExtBot, chat: int, /, reply_to: int = None) -> Message:
        return await bot.send_animation(chat, animation=self.file)


class MessageFragmentAudio(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes

    def __init__(self, file: str | Path | IO[bytes] | InputFile | bytes, update: Update | None = None):
        super().__init__(MessageType.AUDIO, update)
        self.file = file

    async def send(self, bot: ExtBot, chat: int, /, reply_to: int = None) -> Message:
        return await bot.send_audio(chat, audio=self.file)


class MessageFragmentContact(MessageFragment):
    contact: Contact

    def __init__(self, contact: Contact, update: Update | None = None):
        super().__init__(MessageType.CONTACT, update)
        self.contact = contact

    async def send(self, bot: ExtBot, chat: int, /, reply_to: int = None) -> Message:
        return await bot.send_contact(
            chat,
            phone_number=self.contact.phone_number,
            first_name=self.contact.first_name,
            last_name=self.contact.last_name,
        )


class MessageFragmentDice(MessageFragment):
    emoji: str

    def __init__(self, emoji: str, update: Update | None = None):
        super().__init__(MessageType.DICE, update)
        self.emoji = emoji

    async def send(self, bot: ExtBot, chat: int, /, reply_to: int = None) -> Message:
        return await bot.send_dice(chat, emoji=self.emoji)


class MessageFragmentDocument(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes
    caption: str | None

    def __init__(
        self,
        file: str | Path | IO[bytes] | InputFile | bytes,
        caption: str = None,
        update: Update | None = None,
    ):
        super().__init__(MessageType.DOCUMENT, update)
        self.file = file
        self.caption = caption

    async def send(self, bot: ExtBot, chat: int, /, reply_to: int = None) -> Message:
        return await bot.send_document(chat, document=self.file, caption=self.caption)


class MessageFragmentLocation(MessageFragment):
    latitude: float
    longitude: float

    def __init__(self, latitude: float, longitude: float, update: Update | None = None):
        super().__init__(MessageType.LOCATION, update)
        self.latitude = latitude
        self.longitude = longitude

    async def send(self, bot: ExtBot, chat: int, /, reply_to: int = None) -> Message:
        return await bot.send_location(chat, latitude=self.latitude, longitude=self.longitude)


class MessageFragmentVideo(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes
    caption: str | None

    def __init__(
        self,
        file: str | Path | IO[bytes] | InputFile | bytes,
        caption: str = None,
        update: Update | None = None,
    ):
        super().__init__(MessageType.VIDEO, update)
        self.file = file
        self.caption = caption

    async def send(self, bot: ExtBot, chat: int, /, reply_to: int = None) -> Message:
        return await bot.send_video(chat, video=self.file, caption=self.caption)


class MessageFragmentMediaGroup(MessageFragment):
    media: list[MessageFragmentAudio | MessageFragmentDocument | MessageFragmentPhoto | MessageFragmentVideo]
    caption: str | None

    def __init__(
        self,
        media: list[MessageFragmentAudio | MessageFragmentDocument | MessageFragmentPhoto | MessageFragmentVideo],
        caption: str = None,
        update: Update | None = None,
    ):
        super().__init__(_MISSING, update)
        self.media = media
        self.caption = caption

    async def send(self, bot: ExtBot, chat: int, /, reply_to: int = None) -> tuple[Message]:
        media = []
        cord = {
            "photo": InputMediaPhoto,
            "audio": InputMediaAudio,
            "document": InputMediaDocument,
            "video": InputMediaVideo,
        }
        for m in self.media:
            media.append(cord[m.type](m.file))  # Captions should be discarded
        return await bot.send_media_group(chat, media=media, caption=self.caption)


class MessageFragmentSticker(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes

    def __init__(self, file: str | Path | IO[bytes] | InputFile | bytes, update: Update | None = None):
        super().__init__(MessageType.STICKER, update)
        self.file = file

    async def send(self, bot: ExtBot, chat: int, /, reply_to: int = None) -> Message:
        return await bot.send_sticker(chat, sticker=self.file)


class MessageFragmentVenue(MessageFragment):
    latitude: float
    longitude: float
    title: str
    address: str

    def __init__(
        self,
        latitude: float,
        longitude: float,
        title: str,
        address: str,
        update: Update | None = None,
    ):
        super().__init__(MessageType.VENUE, update)
        self.latitude = latitude
        self.longitude = longitude
        self.title = title
        self.address = address

    async def send(self, bot: ExtBot, chat: int, /, reply_to: int = None) -> Message:
        return await bot.send_venue(
            chat,
            latitude=self.latitude,
            longitude=self.longitude,
            title=self.title,
            address=self.address,
        )


PRIORITIES: dict[type[MessageFragment], int] = {
    # Others
    MessageFragmentAnimation: 0,
    MessageFragmentContact: 0,
    MessageFragmentDice: 0,
    MessageFragmentLocation: 0,
    MessageFragmentSticker: 0,
    MessageFragmentVenue: 0,
    # Media Group
    MessageFragmentPhoto: 1,
    MessageFragmentAudio: 1,
    MessageFragmentDocument: 1,
    MessageFragmentVideo: 1,
    MessageFragmentMediaGroup: 1,
    # Text
    MessageFragmentText: float("inf"),  # Always at the end
}
