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
    MessageEntity,
    PhotoSize,
    Sticker,
    Update,
    Video,
    VideoNote,
    Voice,
)
from telegram.constants import MessageType
from telegram.ext import ExtBot
from typing_extensions import Final, Self, TypeVar

from avilla.core import Selector
from avilla.telegram.exception import WrongFragment

_T = TypeVar("_T")


class _FragmentType(str, Enum):
    """Internal use only"""

    REFERENCE = "reference"
    ENTITY = "entity"


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
    def sort(cls, *fragments: _T) -> list[_T]:
        return sorted(fragments, key=lambda f: PRIORITIES[f.__class__])

    @classmethod
    def _compose_text(cls, *fragments: _T) -> list[_T]:
        composed = []
        for fragment in fragments:
            if not isinstance(fragment, (MessageFragmentText, MessageFragmentEntity)):
                composed.append(fragment)
                continue
            if isinstance(fragment, MessageFragmentEntity):
                fragment = fragment.to_text()
            if not composed:
                composed.append(fragment)
            else:
                composed[-1].append_text(fragment)
        return composed

    @classmethod
    def compose(cls, *fragments: _T) -> list[_T]:
        text_type = (MessageFragmentText, MessageFragmentEntity)

        mapping = {
            MessageFragmentPhoto: MessageFragmentMediaGroup,
            MessageFragmentAudio: MessageFragmentAudioGroup,
            MessageFragmentDocument: MessageFragmentMediaGroup,
            MessageFragmentVideo: MessageFragmentMediaGroup,
        }

        fragments = cls._compose_text(*fragments)
        composed = []
        for fragment in fragments:
            if not composed or not isinstance(fragment, tuple(mapping.keys()) + text_type):  # type: ignore
                composed.append(fragment)
                continue
            last_fragment = composed[-1]
            if isinstance(fragment, text_type) and isinstance(last_fragment, CaptionedMessageFragment):
                last_fragment.append_text(fragment)
            elif isinstance(last_fragment, tuple(set(mapping.values()))):
                if (
                    type(last_fragment) is mapping[type(fragment)]
                    and len(last_fragment.media) < last_fragment.SIZE_LIMIT
                ):
                    last_fragment.media.append(fragment)
                    last_fragment.append_text(fragment)
                else:
                    composed.append(fragment)
            elif mapping.get(type(last_fragment)) == mapping[type(fragment)]:
                pop = composed.pop()
                composed.append(mapping[type(fragment)](media=[pop, fragment]))
                composed[-1].append_text(pop)
                composed[-1].append_text(fragment)
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
            if message.caption_entities:
                fragments.extend(
                    MessageFragmentEntity.extract(message.caption, message.caption_entities, update=update)
                )
            else:
                fragments.append(MessageFragmentText(message.caption, update=update))
        return fragments

    def hook(self, fragments: list[Self], params: dict[str, ...] | None = None):
        pass

    def __repr__(self):
        attrs = " ".join(f"{k}={v!r}" for k, v in self.__dict__.items() if k != "update")
        return f"<{self.__class__.__name__} type={self.type} {attrs}>"


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
    entities: list[MessageEntity]

    def __init__(self, text: str, update: Update | None = None, entities: list[MessageEntity] | None = None):
        super().__init__(MessageType.TEXT, update)
        self.text = text
        self.entities = entities or []

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        if message.text:
            if message.entities:
                return MessageFragmentEntity.extract(message.text, message.entities, update)
            return [cls(message.text, update=update)]
        raise WrongFragment

    async def send(
        self, bot: ExtBot, chat: int, /, thread: int | None = None, params: dict[str, ...] | None = None
    ) -> tuple[Message, ...]:
        if not params:
            params = {}
        return (
            await bot.send_message(chat, text=self.text, entities=self.entities, message_thread_id=thread, **params),
        )

    def append_text(self, new: MessageFragmentText):
        text_offset = MessageFragmentEntity.compute_length(self.text)
        if new_entities := new.entities:
            self.entities.extend(
                [
                    MessageEntity(
                        entity.type,
                        entity.offset + text_offset,
                        entity.length,
                        **{k: v for k, v in entity.to_dict().items() if k not in ("type", "offset", "length")},
                    )
                    for entity in new_entities
                ]
            )
        self.text += new.text


class CaptionedMessageFragment(MessageFragment):
    caption: str | None
    caption_entities: list[MessageEntity]

    def append_text(self, new: MessageFragmentText | CaptionedMessageFragment):
        caption = self.caption or ""
        caption_offset = MessageFragmentEntity.compute_length(caption)
        if not self.caption_entities:
            self.caption_entities = []
        if new_entities := (new.entities if isinstance(new, MessageFragmentText) else new.caption_entities):
            self.caption_entities.extend(
                [
                    MessageEntity(
                        entity.type,
                        entity.offset + caption_offset,
                        entity.length,
                        **{k: v for k, v in entity.to_dict().items() if k not in ("type", "offset", "length")},
                    )
                    for entity in new_entities
                ]
            )
        self.caption = caption + (new.text if isinstance(new, MessageFragmentText) else new.caption or "")


class MessageFragmentPhoto(CaptionedMessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes | PhotoSize
    has_spoiler: bool

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
                caption_entities=self.caption_entities,
                message_thread_id=thread,
                has_spoiler=self.has_spoiler,
                **params,
            ),
        )


class MessageFragmentAudio(CaptionedMessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes | Audio

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
        return (
            await bot.send_audio(
                chat,
                audio=self.file,
                caption=self.caption,
                caption_entities=self.caption_entities,
                message_thread_id=thread,
                **params,
            ),
        )


class MessageFragmentVideo(CaptionedMessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes | Video
    has_spoiler: bool

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
                caption_entities=self.caption_entities,
                message_thread_id=thread,
                has_spoiler=self.has_spoiler,
                **params,
            ),
        )


class MessageFragmentAnimation(CaptionedMessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes | Animation
    has_spoiler: bool

    def __init__(
        self,
        file: str | Path | IO[bytes] | InputFile | bytes | Animation,
        has_spoiler: bool,
        caption: str | None = None,
        update: Update | None = None,
    ):
        super().__init__(MessageType.ANIMATION, update)
        self.file = file
        self.has_spoiler = has_spoiler
        self.caption = caption

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
                chat,
                animation=self.file,
                caption=self.caption,
                caption_entities=self.caption_entities,
                message_thread_id=thread,
                has_spoiler=self.has_spoiler,
                **params,
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


class MessageFragmentDocument(CaptionedMessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes | Document

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
            await bot.send_document(
                chat,
                document=self.file,
                caption=self.caption,
                caption_entities=self.caption_entities,
                message_thread_id=thread,
                **params,
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


class MessageFragmentGroup(CaptionedMessageFragment):
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
        return await bot.send_media_group(
            chat,
            media=media,
            caption=self.caption,
            caption_entities=self.caption_entities,
            message_thread_id=thread,
            **params,
        )


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
        return await bot.send_media_group(
            chat,
            media=media,
            caption=self.caption,
            caption_entities=self.caption_entities,
            message_thread_id=thread,
            **params,
        )


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


class MessageFragmentVoice(CaptionedMessageFragment):
    file: str | Path | IO[bytes] | InputFile | bytes | Voice

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
        return (
            await bot.send_voice(
                chat,
                voice=self.file,
                caption=self.caption,
                caption_entities=self.caption_entities,
                message_thread_id=thread,
                **params,
            ),
        )


class MessageFragmentEntity(MessageFragment):
    data: dict[str, ...]
    raw: MessageEntity
    text: str
    e_type: str

    @property
    def type(self):
        return f"entity.{self.e_type}"

    @type.setter
    def type(self, value):
        pass

    def __init__(
        self,
        text: str,
        type: str,
        data: dict[str, ...],
        raw: MessageEntity | None = None,
        update: Update | None = None,
    ):
        super().__init__(_FragmentType.ENTITY, update)
        self.text = text
        self.e_type = type
        self.raw = raw
        self.data = data

    @classmethod
    def extract(
        cls, text: str, entities: tuple[MessageEntity, ...], update: Update | None = None
    ) -> list[Self | MessageFragmentText]:
        # See: https://core.telegram.org/api/entities#entity-length
        result = []
        text = text.encode("utf-16be")
        remaining = text
        offset = 0
        ignored_keys = ("type", "offset", "length")
        for entity in entities:
            start = (entity.offset - offset) * 2
            end = (entity.offset - offset + entity.length) * 2
            if left := remaining[:start]:
                result.append(MessageFragmentText(left.decode("utf-16be"), update))
            result.append(
                MessageFragmentEntity(
                    remaining[start:end].decode("utf-16be"),
                    entity.type,
                    {k: v for k, v in entity.to_dict().items() if k not in ignored_keys},
                    entity,
                    update,
                )
            )
            remaining = remaining[end:]
            offset = entity.offset + entity.length
        if remaining:
            result.append(MessageFragmentText(remaining.decode("utf-16be"), update))
        return result

    @staticmethod
    def compute_length(text: str) -> int:
        # See: https://core.telegram.org/api/entities#computing-entity-length
        text = text.encode("utf-8")
        return sum(2 if byte >= 0xF0 else 1 for byte in text if (byte & 0xC0) != 0x80)

    @classmethod
    def decompose(cls, message: Message, update: Update | None = None) -> list[Self]:
        raise WrongFragment

    def to_text(self) -> MessageFragmentText:
        return MessageFragmentText(
            self.text,
            update=self.update,
            entities=[MessageEntity(self.e_type, 0, self.compute_length(self.text), **self.data)],
        )


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
