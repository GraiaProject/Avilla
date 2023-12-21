from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Final

from graia.amnesia.message.element import Element

from avilla.core.elements import Audio
from avilla.core.elements import Picture as CorePicture
from avilla.core.elements import Reference as CoreReference
from avilla.core.elements import Video as CoreVideo
from avilla.core.resource import LocalFileResource, Resource


class Reference(CoreReference):
    original: ...


class Picture(CorePicture):
    has_spoiler: bool

    def __init__(self, resource: Resource[bytes] | Resource[str] | Path | str, has_spoiler: bool = False):
        if isinstance(resource, Path):
            resource = LocalFileResource(resource)
        elif isinstance(resource, str):
            resource = LocalFileResource(Path(resource))
        self.resource = resource
        self.has_spoiler = has_spoiler

    def __repr__(self):
        return f"[$Picture:resource={self.resource.to_selector()};has_spoiler={self.has_spoiler}]"


class Video(CoreVideo):
    has_spoiler: bool

    def __init__(self, resource: Resource[bytes] | Path | str, has_spoiler: bool = False):
        if isinstance(resource, Path):
            resource = LocalFileResource(resource)
        elif isinstance(resource, str):
            resource = LocalFileResource(Path(resource))
        self.resource = resource
        self.has_spoiler = has_spoiler

    def __repr__(self):
        return f"[$Video:resource={self.resource.to_selector()};has_spoiler={self.has_spoiler}]"


class Animation(Element):
    resource: Resource[bytes] | Path | str
    width: int
    height: int
    duration: int
    has_spoiler: bool

    def __init__(
        self,
        resource: Resource[bytes] | Path | str,
        width: int = -1,
        height: int = -1,
        duration: int = -1,
        has_spoiler: bool = None,
    ):
        if isinstance(resource, Path):
            resource = LocalFileResource(resource)
        elif isinstance(resource, str):
            resource = LocalFileResource(Path(resource))
        self.resource = resource
        self.width = width
        self.height = height
        self.duration = duration
        self.has_spoiler = has_spoiler

    def __str__(self) -> str:
        return "[$Animation]"

    def __repr__(self):
        return f"[$Animation:resource={self.resource.to_selector()};has_spoiler={self.has_spoiler}]"


@dataclass
class Contact(Element):
    phone_number: str
    first_name: str
    last_name: str | None = None
    user_id: int | None = None
    vcard: str | None = None

    def __str__(self) -> str:
        return "[$Contact]"


@dataclass
class Location(Element):
    latitude: float
    longitude: float

    def __str__(self) -> str:
        return "[$Location]"


@dataclass
class Sticker(Element):
    resource: Resource[bytes] | Path | str
    width: int = -1
    height: int = -1
    is_animated: bool = None
    is_video: bool = None

    def __str__(self) -> str:
        return "[$Sticker]"

    def __repr__(self):
        return f"[$Sticker:resource={self.resource.to_selector()}]"


@dataclass
class Venue(Element):
    latitude: float
    longitude: float
    title: str
    address: str

    def __str__(self) -> str:
        return "[$Venue]"


class VideoNote(CoreVideo):
    def __str__(self) -> str:
        return "[$VideoNote]"


class Voice(Audio):
    def __str__(self) -> str:
        return "[$Voice]"


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


@dataclass
class Entity(Element):
    offset: int
    length: int
    text: str

    def __str__(self):
        return f"[${self.__class__.__name__}]"

    def __repr__(self):
        return f"[${self.__class__.__name__}:offset={self.offset};length={self.length};text={self.text}]"


@dataclass
class EntityHashTag(Entity):
    type: Final[str] = MessageEntityType.HASH_TAG


@dataclass
class EntityCashTag(Entity):
    type: Final[str] = MessageEntityType.CASHTAG


@dataclass
class EntityPhoneNumber(Entity):
    type: Final[str] = MessageEntityType.PHONE_NUMBER


@dataclass
class EntityBotCommand(Entity):
    type: Final[str] = MessageEntityType.BOT_COMMAND


@dataclass
class EntityUrl(Entity):
    type: Final[str] = MessageEntityType.URL


@dataclass
class EntityEmail(Entity):
    type: Final[str] = MessageEntityType.EMAIL


@dataclass
class EntityBold(Entity):
    type: Final[str] = MessageEntityType.BOLD


@dataclass
class EntityItalic(Entity):
    type: Final[str] = MessageEntityType.ITALIC


@dataclass
class EntityCode(Entity):
    type: Final[str] = MessageEntityType.CODE


@dataclass
class EntityPre(Entity):
    language: str
    type: Final[str] = MessageEntityType.PRE


@dataclass
class EntityTextLink(Entity):
    url: str
    type: Final[str] = MessageEntityType.TEXT_LINK


@dataclass
class EntityUnderline(Entity):
    type: Final[str] = MessageEntityType.UNDERLINE


@dataclass
class EntityStrikeThrough(Entity):
    type: Final[str] = MessageEntityType.STRIKETHROUGH


@dataclass
class EntitySpoiler(Entity):
    type: Final[str] = MessageEntityType.SPOILER


class Invoice(Element):
    # To be implemented
    ...


class Game(Element):
    # To be implemented
    ...
