from __future__ import annotations

from contextlib import suppress
from enum import Enum
from pathlib import Path
from typing import IO

from telegram import (
    Animation,
    Audio,
    Document,
    InputFile,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
    PhotoSize,
    Sticker,
    Update,
    Video,
    VideoNote,
    Voice,
)
from telegram.constants import MessageType
from telegram.ext import ExtBot
from typing_extensions import Final, Self

from avilla.core import Selector
from avilla.telegram.exception import WrongFragment


class _FragmentType(str, Enum):
    """Internal use only"""

    REFERENCE = "reference"


class MessageFragment:
    type: MessageType
    update: Update | None

    def __init__(self, msg_type: MessageType | _FragmentType | None, update: Update | None = None):
        self.type = msg_type
        self.update = update

    def __getitem__(self, item):
        return self.__getattribute__(item)

    async def send(
        self, bot: ExtBot, chat: int, /, thread: int | None = None, params: dict[str, ...] | None = None
    ) -> tuple[Message, ...]:
        ...

    @classmethod
    def sort(cls, *fragments: Self) -> list[Self]:
        return sorted(fragments, key=lambda f: PRIORITIES[f.__class__])

    @classmethod
    def compose(cls, *fragments: Self) -> list[Self]:
        text_type = (MessageFragmentText,)

        mapping = {
            MessageFragmentPhoto: MessageFragmentMediaGroup,
            MessageFragmentAudio: MessageFragmentAudioGroup,
            MessageFragmentDocument: MessageFragmentMediaGroup,
            MessageFragmentVideo: MessageFragmentMediaGroup,
        }

        composed = []
        for fragment in fragments:
            if not composed or not isinstance(fragment, tuple(mapping.keys()) + text_type):
                composed.append(fragment)
                continue
            last_fragment = composed[-1]
            if isinstance(fragment, text_type):
                if last_fragment.type == MessageType.TEXT:
                    last_fragment.text += fragment.text
                elif getattr(last_fragment, "caption", -1) != -1:
                    last_fragment.caption = (last_fragment.caption or "") + fragment.text
                else:
                    composed.append(fragment)
            elif isinstance(last_fragment, tuple(set(mapping.values()))):
                if (
                    type(last_fragment) is mapping[type(fragment)]
                    and len(last_fragment.media) < last_fragment.SIZE_LIMIT
                ):
                    last_fragment.media.append(fragment)
                    last_fragment.caption = (last_fragment.caption or "") + (fragment.caption or "") or None
                else:
                    composed.append(fragment)
            elif mapping.get(type(last_fragment)) == mapping[type(fragment)]:
                pop = composed.pop()
                composed.append(
                    mapping[type(fragment)](
                        media=[pop, fragment], caption=(pop.caption or "") + (fragment.caption or "") or None
                    )
                )
            else:
                composed.append(fragment)
        return composed

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        fragments = []
        for sub in cls.__subclasses__():
            with suppress(WrongFragment):
                if frag := sub.decompose(message, update=update):
                    fragments.extend(frag)
        if message.caption:
            fragments.append(MessageFragmentText(message.caption, update=update))
        return fragments

    def hook(self, fragments: list[Self], params: dict[str, ...] | None = None):
        pass


class MessageFragmentReference(MessageFragment):
    selector: Selector | None
    original: Message | None

    def __init__(self, selector: Selector | None = None, original: Message | None = None, update: Update | None = None):
        super().__init__(_FragmentType.REFERENCE, update)
        self.selector = selector
        self.original = original

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        if message.reply_to_message:
            return [cls(None, original=message.reply_to_message, update=update)]
        raise WrongFragment

    def hook(self, fragments: list[MessageFragment], params: dict[str, ...] | None = None):
        if self.selector:
            params["reply_to_message_id"] = self.selector.pattern["message"].split(",")[0]
        elif self.original:
            params["reply_to_message_id"] = self.original.message_id
        fragments.remove(self)


class MessageFragmentText(MessageFragment):
    text: str

    def __init__(self, text: str, update: Update | None = None):
        super().__init__(MessageType.TEXT, update)
        self.text = text

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        if message.text:
            return [cls(message.text, update=update)]
        raise WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, thread: int | None = None, params: dict[str, ...] | None = None
    ) -> tuple[Message, ...]:
        if not params:
            params = {}
        return (await bot.send_message(chat, text=self.text, message_thread_id=thread, **params),)


class MessageFragmentPhoto(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes | PhotoSize
    has_spoiler: bool
    caption: str | None

    def __init__(
        self,
        file: str | Path | IO[bytes] | InputFile | bytes | PhotoSize,
        has_spoiler: bool,
        caption: str | None = None,
        update: Update | None = None,
    ):
        super().__init__(MessageType.PHOTO, update)
        self.file = file
        self.has_spoiler = has_spoiler
        self.caption = caption

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        if message.photo:
            return [MessageFragmentPhoto(message.photo[-1], has_spoiler=message.has_media_spoiler, update=update)]
        raise WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, thread: int | None = None, params: dict[str, ...] | None = None
    ) -> tuple[Message, ...]:
        if not params:
            params = {}
        return (
            await bot.send_photo(
                chat,
                photo=self.file,
                caption=self.caption,
                message_thread_id=thread,
                has_spoiler=self.has_spoiler,
                **params,
            ),
        )


class MessageFragmentAudio(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes | Audio
    caption: str | None

    def __init__(
        self,
        file: str | Path | IO[bytes] | InputFile | bytes | Audio,
        caption: str | None = None,
        update: Update | None = None,
    ):
        super().__init__(MessageType.AUDIO, update)
        self.file = file
        self.caption = caption

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        if message.audio:
            return [cls(message.audio, update=update)]
        raise WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, thread: int | None = None, params: dict[str, ...] | None = None
    ) -> tuple[Message, ...]:
        if not params:
            params = {}
        return (await bot.send_audio(chat, audio=self.file, caption=self.caption, message_thread_id=thread, **params),)


class MessageFragmentVideo(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes | Video
    has_spoiler: bool
    caption: str | None

    def __init__(
        self,
        file: str | Path | IO[bytes] | InputFile | bytes | Video,
        has_spoiler: bool,
        caption: str | None = None,
        update: Update | None = None,
    ):
        super().__init__(MessageType.VIDEO, update)
        self.file = file
        self.has_spoiler = has_spoiler
        self.caption = caption

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        if message.video:
            return [cls(message.video, has_spoiler=message.has_media_spoiler, update=update)]
        raise WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, thread: int | None = None, params: dict[str, ...] | None = None
    ) -> tuple[Message, ...]:
        if not params:
            params = {}
        return (
            await bot.send_video(
                chat,
                video=self.file,
                caption=self.caption,
                message_thread_id=thread,
                has_spoiler=self.has_spoiler,
                **params,
            ),
        )


class MessageFragmentAnimation(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes | Animation
    has_spoiler: bool

    def __init__(
        self,
        file: str | Path | IO[bytes] | InputFile | bytes | Animation,
        has_spoiler: bool,
        update: Update | None = None,
    ):
        super().__init__(MessageType.ANIMATION, update)
        self.file = file
        self.has_spoiler = has_spoiler

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        if message.animation:
            return [cls(message.animation, has_spoiler=message.has_media_spoiler, update=update)]
        raise WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, thread: int | None = None, params: dict[str, ...] | None = None
    ) -> tuple[Message, ...]:
        if not params:
            params = {}
        return (
            await bot.send_animation(
                chat, animation=self.file, message_thread_id=thread, has_spoiler=self.has_spoiler, **params
            ),
        )


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
        raise WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, thread: int | None = None, params: dict[str, ...] | None = None
    ) -> tuple[Message, ...]:
        if not params:
            params = {}
        return (
            await bot.send_contact(
                chat,
                phone_number=self.phone_number,
                first_name=self.first_name,
                last_name=self.last_name,
                vcard=self.vcard,
                message_thread_id=thread,
                **params,
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
        raise WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, thread: int | None = None, params: dict[str, ...] | None = None
    ) -> tuple[Message, ...]:
        if not params:
            params = {}
        return (await bot.send_dice(chat, emoji=self.emoji, message_thread_id=thread, **params),)


class MessageFragmentDocument(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes | Document
    caption: str | None

    def __init__(
        self,
        file: str | Path | IO[bytes] | InputFile | bytes | Document,
        caption: str | None = None,
        update: Update | None = None,
    ):
        super().__init__(MessageType.DOCUMENT, update)
        self.file = file
        self.caption = caption

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        if message.document:
            return [cls(message.document, update=update)]
        raise WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, thread: int | None = None, params: dict[str, ...] | None = None
    ) -> tuple[Message, ...]:
        if not params:
            params = {}
        return (
            await bot.send_document(chat, document=self.file, caption=self.caption, message_thread_id=thread, **params),
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
        raise WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, thread: int | None = None, params: dict[str, ...] | None = None
    ) -> tuple[Message, ...]:
        if not params:
            params = {}
        return (
            await bot.send_location(
                chat,
                latitude=self.latitude,
                longitude=self.longitude,
                message_thread_id=thread,
                **params,
            ),
        )


class MessageFragmentGroup(MessageFragment):
    SIZE_LIMIT: Final[int] = 9
    media: list[MessageFragment]


class MessageFragmentMediaGroup(MessageFragmentGroup):
    media: list[MessageFragmentDocument | MessageFragmentPhoto | MessageFragmentVideo]
    caption: str | None

    def __init__(
        self,
        media: list[MessageFragmentDocument | MessageFragmentPhoto | MessageFragmentVideo],
        caption: str | None = None,
        update: Update | None = None,
    ):
        super().__init__(None, update)
        self.media = media
        self.caption = caption

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        # Media Group is not meant to be decomposed, since it's already decomposed upon receiving
        raise WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, thread: int | None = None, params: dict[str, ...] | None = None
    ) -> tuple[Message, ...]:
        if not params:
            params = {}
        mapping = {
            MessageType.PHOTO: InputMediaPhoto,
            MessageType.DOCUMENT: InputMediaDocument,
            MessageType.VIDEO: InputMediaVideo,
        }
        media = [mapping[m.type](m.file, has_spoiler=m.has_spoiler) for m in self.media]  # Captions should be discarded
        return await bot.send_media_group(chat, media=media, caption=self.caption, message_thread_id=thread, **params)


class MessageFragmentAudioGroup(MessageFragmentGroup):
    media: list[MessageFragmentAudio]
    caption: str | None

    def __init__(
        self,
        media: list[MessageFragmentAudio],
        caption: str | None = None,
        update: Update | None = None,
    ):
        super().__init__(None, update)
        self.media = media
        self.caption = caption

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        # Media Group is not meant to be decomposed, since it's already decomposed upon receiving
        raise WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, thread: int | None = None, params: dict[str, ...] | None = None
    ) -> tuple[Message, ...]:
        if not params:
            params = {}
        media = [InputMediaAudio(m.file) for m in self.media]
        return await bot.send_media_group(chat, media=media, caption=self.caption, message_thread_id=thread, **params)


class MessageFragmentSticker(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes | Sticker

    def __init__(self, file: str | Path | IO[bytes] | InputFile | bytes | Sticker, update: Update | None = None):
        super().__init__(MessageType.STICKER, update)
        self.file = file

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        if message.sticker:
            return [cls(message.sticker, update=update)]
        raise WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, thread: int | None = None, params: dict[str, ...] | None = None
    ) -> tuple[Message, ...]:
        if not params:
            params = {}
        return (await bot.send_sticker(chat, sticker=self.file, message_thread_id=thread, **params),)


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
        raise WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, thread: int | None = None, params: dict[str, ...] | None = None
    ) -> tuple[Message, ...]:
        if not params:
            params = {}
        return (
            await bot.send_venue(
                chat,
                latitude=self.latitude,
                longitude=self.longitude,
                title=self.title,
                address=self.address,
                message_thread_id=thread,
                **params,
            ),
        )


class MessageFragmentVideoNote(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes | VideoNote

    def __init__(
        self,
        file: str | Path | IO[bytes] | InputFile | bytes | VideoNote,
        update: Update | None = None,
    ):
        super().__init__(MessageType.VIDEO_NOTE, update)
        self.file = file

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        if message.video_note:
            return [cls(message.video_note, update=update)]
        raise WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, thread: int | None = None, params: dict[str, ...] | None = None
    ) -> tuple[Message, ...]:
        if not params:
            params = {}
        return (
            await bot.send_video_note(
                chat,
                video_note=self.file,
                message_thread_id=thread,
                **params,
            ),
        )


class MessageFragmentVoice(MessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes | Voice
    caption: str | None

    def __init__(
        self,
        file: str | Path | IO[bytes] | InputFile | bytes | Voice,
        caption: str | None = None,
        update: Update | None = None,
    ):
        super().__init__(MessageType.VOICE, update)
        self.file = file
        self.caption = caption

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        if message.voice:
            return [cls(message.voice, update=update)]
        raise WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, thread: int | None = None, params: dict[str, ...] | None = None
    ) -> tuple[Message, ...]:
        if not params:
            params = {}
        return (await bot.send_voice(chat, voice=self.file, caption=self.caption, message_thread_id=thread, **params),)


PRIORITIES: dict[type[MessageFragment], int | float] = {
    # Reply Hook (Non-telegram standard)
    MessageFragmentReference: -1,  # Anywhere is fine
    # Others
    MessageFragmentAnimation: 0,
    MessageFragmentContact: 0,
    MessageFragmentDice: 0,
    MessageFragmentLocation: 0,
    MessageFragmentSticker: 0,
    MessageFragmentVenue: 0,
    # Media Group
    MessageFragmentPhoto: 1,
    MessageFragmentDocument: 1,
    MessageFragmentVideo: 1,
    MessageFragmentVideoNote: 1,
    MessageFragmentVoice: 1,
    MessageFragmentGroup: 1,
    MessageFragmentMediaGroup: 1,
    # Audio Group
    MessageFragmentAudio: 2,
    MessageFragmentAudioGroup: 2,
    # Text
    MessageFragmentText: float("inf"),  # Always at the end
}
