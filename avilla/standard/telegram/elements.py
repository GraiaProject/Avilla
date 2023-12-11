from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import IO, Literal, overload

from graia.amnesia.message.element import Element

from avilla.core import Audio, Video


class _TObject:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class _FileObject(_TObject):
    file_id: str
    file_unique_id: str

    def __hash__(self):
        return hash(f"[{self.__class__.__name__}:file_unique_id={self.file_unique_id}]")

    def __eq__(self, other):
        if not getattr(other, "file_unique_id", None):
            return False
        return self.file_unique_id == other.file_unique_id


class Animation(_FileObject, Element):
    width: int
    height: int
    is_animated: bool
    is_video: bool
    from_input: IO[bytes] | bytes | str | Path

    @overload
    def __init__(
        self,
        /,
        file_id: str,
        file_unique_id: str,
        width: int = None,
        height: int = None,
        is_animated: bool = None,
        is_video: bool = None,
    ):
        ...

    @overload
    def __init__(
        self,
        /,
        from_input: IO[bytes] | bytes | str | Path,
    ):
        ...

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __str__(self) -> str:
        return f"[$Animation]"


@dataclass
class Contact(Element):
    phone_number: str
    first_name: str
    last_name: str | None = None
    user_id: int | None = None
    vcard: str | None = None

    def __str__(self) -> str:
        return f"[$Contact]"


class Document(_FileObject, Element):
    from_input: IO[bytes] | bytes | str | Path

    @overload
    def __init__(
        self,
        /,
        file_id: str,
        file_unique_id: str,
    ):
        ...

    @overload
    def __init__(
        self,
        /,
        from_input: IO[bytes] | bytes | str | Path,
    ):
        ...

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __str__(self) -> str:
        return f"[$Document]"


@dataclass
class Location(Element):
    latitude: float
    longitude: float

    def __str__(self) -> str:
        return f"[$Location]"


@dataclass
class Sticker(_FileObject, Element):
    width: int
    height: int
    is_animated: bool
    is_video: bool

    def __str__(self) -> str:
        return f"[$Sticker]"


@dataclass
class Venue(Element):
    latitude: float
    longitude: float
    title: str
    address: str

    def __str__(self) -> str:
        return f"[$Venue]"


class VideoNote(Video):
    def __str__(self) -> str:
        return f"[$VideoNote]"


class Voice(Audio):
    def __str__(self) -> str:
        return f"[$Voice]"


class DiceEmoji(str, Enum):
    DICE = "🎲"
    DARTS = "🎯"
    BASKETBALL = "🏀"
    FOOTBALL = "⚽"
    SLOT_MACHINE = "🎰"
    BOWLING = "🎳"


class DiceLimit(int, Enum):
    MIN_VALUE = 1
    MAX_VALUE_DICE = 6
    MAX_VALUE_DARTS = 6
    MAX_VALUE_BASKETBALL = 5
    MAX_VALUE_FOOTBALL = 5
    MAX_VALUE_SLOT_MACHINE = 64
    MAX_VALUE_BOWLING = 6


class Dice(Element):
    value: int | None
    emoji: DiceEmoji

    def __init__(self, emoji: DiceEmoji = DiceEmoji.DICE, value: int = None):
        self.emoji = emoji
        self.value = value

    @property
    def max_value(self) -> DiceLimit:
        return getattr(DiceLimit, f"MAX_VALUE_{self.emoji.name}")

    @property
    def min_value(self) -> DiceLimit:
        return DiceLimit.MIN_VALUE

    def __str__(self) -> str:
        return f"[${self.emoji.value}:value={self.value}]"


class Story(Element):
    """Currently holds no information."""


class MessageEntityType(str, Enum):
    MENTION = "mention"
    HASH_TAG = "hashtag"
    CASHTAG = "cashtag"
    PHONE_NUMBER = "phone_number"
    BOT_COMMAND = "bot_command"
    URL = "url"
    EMAIL = "email"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    PRE = "pre"
    TEXT_LINK = "text_link"
    TEXT_MENTION = "text_mention"
    UNDERLINE = "underline"
    STRIKETHROUGH = "strikethrough"
    SPOILER = "spoiler"
    CUSTOM_EMOJI = "custom_emoji"


class Entity(_TObject, Element):
    text: str = None
    language: str = None
    url: str = None
    user: str = None
    custom_emoji_id: str = None

    @overload
    def __init__(self, kind: Literal[MessageEntityType.PRE], text: str, language: str):
        ...

    @overload
    def __init__(self, kind: Literal[MessageEntityType.TEXT_LINK], text: str, url: str):
        ...

    @overload
    def __init__(self, kind: Literal[MessageEntityType.TEXT_MENTION], text: str, user: ...):
        ...

    @overload
    def __init__(self, kind: Literal[MessageEntityType.CUSTOM_EMOJI], text: str, custom_emoji_id: str):
        ...

    @overload
    def __init__(self, kind: MessageEntityType, text: str):
        ...

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Invoice(Element):
    # To be implemented
    ...


class Game(Element):
    # To be implemented
    ...
