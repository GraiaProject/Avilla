from __future__ import annotations

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
from typing_extensions import Final, Self


class _WrongFragment(Exception):
    ...


class MessageFragment:
    type: MessageType
    update: Update | None

    def __init__(self, msg_type: MessageType | None, update: Update | None = None):
        self.type = msg_type
        self.update = update

    def __getitem__(self, item):
        return self.__getattribute__(item)

    async def send(
        self, bot: ExtBot, chat: int, /, reply_to: int | None = None, thread: int | None = None
    ) -> tuple[Message, ...]:
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
                    if len(composed[-1].media) < MessageFragmentMediaGroup.SIZE_LIMIT:
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
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        fragments = []
        for sub in cls.__subclasses__():
            try:
                fragments.extend(sub.decompose(message, update=update))
            except _WrongFragment:
                pass
        return fragments


class MessageFragmentText(MessageFragment):
    text: str

    def __init__(self, text: str, update: Update | None = None):
        super().__init__(MessageType.TEXT, update)
        self.text = text

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        if message.text:
            return [cls(message.text, update=update)]
        raise _WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, reply_to: int | None = None, thread: int | None = None
    ) -> tuple[Message, ...]:
        return (await bot.send_message(chat, text=self.text, reply_to_message_id=reply_to, message_thread_id=thread),)


class MessageFragmentPhoto(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes | PhotoSize
    caption: str | None

    def __init__(
        self,
        file: str | Path | IO[bytes] | InputFile | bytes | PhotoSize,
        caption: str | None = None,
        update: Update | None = None,
    ):
        super().__init__(MessageType.PHOTO, update)
        self.file = file
        self.caption = caption

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        if message.photo:
            if message.caption:
                return [cls(message.photo[-1], update=update), MessageFragmentText(message.caption, update=update)]
            else:
                return [MessageFragmentPhoto(message.photo[-1], update=update)]
        raise _WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, reply_to: int | None = None, thread: int | None = None
    ) -> tuple[Message, ...]:
        return (
            await bot.send_photo(
                chat, photo=self.file, caption=self.caption, reply_to_message_id=reply_to, message_thread_id=thread
            ),
        )


class MessageFragmentAnimation(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes

    def __init__(self, file: str | Path | IO[bytes] | InputFile | bytes, update: Update | None = None):
        super().__init__(MessageType.ANIMATION, update)
        self.file = file

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        raise _WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, reply_to: int | None = None, thread: int | None = None
    ) -> tuple[Message, ...]:
        return (
            await bot.send_animation(chat, animation=self.file, reply_to_message_id=reply_to, message_thread_id=thread),
        )


class MessageFragmentAudio(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes

    def __init__(self, file: str | Path | IO[bytes] | InputFile | bytes, update: Update | None = None):
        super().__init__(MessageType.AUDIO, update)
        self.file = file

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        raise _WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, reply_to: int | None = None, thread: int | None = None
    ) -> tuple[Message, ...]:
        return (await bot.send_audio(chat, audio=self.file, reply_to_message_id=reply_to, message_thread_id=thread),)


class MessageFragmentContact(MessageFragment):
    phone_number: str
    first_name: str
    last_name: str | None = None
    user_id: int | None = None
    vcard: str | None = None

    def __init__(
        self,
        phone_number: str,
        first_name: str,
        last_name: str | None = None,
        user_id: int | None = None,
        vcard: str | None = None,
        update: Update | None = None,
    ):
        super().__init__(MessageType.CONTACT, update)
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
        self.user_id = user_id
        self.vcard = vcard

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        if message.contact:
            return [
                cls(
                    message.contact.phone_number,
                    message.contact.first_name,
                    message.contact.last_name,
                    message.contact.user_id,
                    message.contact.vcard,
                    update=update,
                )
            ]
        raise _WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, reply_to: int | None = None, thread: int | None = None
    ) -> tuple[Message, ...]:
        return (
            await bot.send_contact(
                chat,
                phone_number=self.phone_number,
                first_name=self.first_name,
                last_name=self.last_name,
                vcard=self.vcard,
                reply_to_message_id=reply_to,
                message_thread_id=thread,
            ),
        )


class MessageFragmentDice(MessageFragment):
    emoji: str
    value: int | None

    def __init__(self, emoji: str, value: int | None = None, update: Update | None = None):
        super().__init__(MessageType.DICE, update)
        self.emoji = emoji
        self.value = value

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        if message.dice:
            return [cls(message.dice.emoji, message.dice.value, update=update)]
        raise _WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, reply_to: int | None = None, thread: int | None = None
    ) -> tuple[Message, ...]:
        return (await bot.send_dice(chat, emoji=self.emoji, reply_to_message_id=reply_to, message_thread_id=thread),)


class MessageFragmentDocument(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes
    caption: str | None

    def __init__(
        self,
        file: str | Path | IO[bytes] | InputFile | bytes,
        caption: str | None = None,
        update: Update | None = None,
    ):
        super().__init__(MessageType.DOCUMENT, update)
        self.file = file
        self.caption = caption

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        raise _WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, reply_to: int | None = None, thread: int | None = None
    ) -> tuple[Message, ...]:
        return (
            await bot.send_document(
                chat, document=self.file, caption=self.caption, reply_to_message_id=reply_to, message_thread_id=thread
            ),
        )


class MessageFragmentLocation(MessageFragment):
    latitude: float
    longitude: float

    def __init__(self, latitude: float, longitude: float, update: Update | None = None):
        super().__init__(MessageType.LOCATION, update)
        self.latitude = latitude
        self.longitude = longitude

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        if message.location:
            return [cls(message.location.latitude, message.location.longitude, update=update)]
        raise _WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, reply_to: int | None = None, thread: int | None = None
    ) -> tuple[Message, ...]:
        return (
            await bot.send_location(
                chat,
                latitude=self.latitude,
                longitude=self.longitude,
                reply_to_message_id=reply_to,
                message_thread_id=thread,
            ),
        )


class MessageFragmentVideo(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes
    caption: str | None

    def __init__(
        self,
        file: str | Path | IO[bytes] | InputFile | bytes,
        caption: str | None = None,
        update: Update | None = None,
    ):
        super().__init__(MessageType.VIDEO, update)
        self.file = file
        self.caption = caption

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        raise _WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, reply_to: int | None = None, thread: int | None = None
    ) -> tuple[Message, ...]:
        return (
            await bot.send_video(
                chat, video=self.file, caption=self.caption, reply_to_message_id=reply_to, message_thread_id=thread
            ),
        )


class MessageFragmentMediaGroup(MessageFragment):
    SIZE_LIMIT: Final[int] = 9
    media: list[MessageFragmentAudio | MessageFragmentDocument | MessageFragmentPhoto | MessageFragmentVideo]
    caption: str | None

    def __init__(
        self,
        media: list[MessageFragmentAudio | MessageFragmentDocument | MessageFragmentPhoto | MessageFragmentVideo],
        caption: str | None = None,
        update: Update | None = None,
    ):
        super().__init__(None, update)
        self.media = media
        self.caption = caption

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        raise _WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, reply_to: int | None = None, thread: int | None = None
    ) -> tuple[Message, ...]:
        media = []
        cord = {
            "photo": InputMediaPhoto,
            "audio": InputMediaAudio,
            "document": InputMediaDocument,
            "video": InputMediaVideo,
        }
        for m in self.media:
            media.append(cord[m.type](m.file))  # Captions should be discarded
        return await bot.send_media_group(
            chat, media=media, caption=self.caption, reply_to_message_id=reply_to, message_thread_id=thread
        )


class MessageFragmentSticker(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes

    def __init__(self, file: str | Path | IO[bytes] | InputFile | bytes, update: Update | None = None):
        super().__init__(MessageType.STICKER, update)
        self.file = file

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        raise _WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, reply_to: int | None = None, thread: int | None = None
    ) -> tuple[Message, ...]:
        return (
            await bot.send_sticker(chat, sticker=self.file, reply_to_message_id=reply_to, message_thread_id=thread),
        )


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

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        if message.venue:
            return [
                cls(
                    message.venue.location.latitude,
                    message.venue.location.longitude,
                    message.venue.title,
                    message.venue.address,
                    update=update,
                )
            ]
        raise _WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, reply_to: int | None = None, thread: int | None = None
    ) -> tuple[Message, ...]:
        return (
            await bot.send_venue(
                chat,
                latitude=self.latitude,
                longitude=self.longitude,
                title=self.title,
                address=self.address,
                reply_to_message_id=reply_to,
                message_thread_id=thread,
            ),
        )


PRIORITIES: dict[type[MessageFragment], int | float] = {
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
