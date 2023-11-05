from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final

from graia.amnesia.message.element import Element, Text

from avilla.core import Audio, Notice, Video


@dataclass
class FileObject:
    file_id: str
    file_unique_id: str


@dataclass
class Animation(FileObject, Element):
    width: int
    height: int
    is_animated: bool
    is_video: bool

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


@dataclass
class Document(FileObject, Element):
    def __str__(self) -> str:
        return f"[$Document]"


@dataclass
class Location(Element):
    latitude: float
    longitude: float

    def __str__(self) -> str:
        return f"[$Location]"


@dataclass
class Sticker(FileObject, Element):
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
    DICE = "Dice"
    """ 🎲 """

    DARTS = "Darts"
    """ 🎯 """

    BASKETBALL = "Basketball"
    """ 🏀 """

    FOOTBALL = "Football"
    """ ⚽ """

    SLOT_MACHINE = "SlotMachine"
    """ 🎰 """

    BOWLING = "Bowling"
    """ 🎳 """


class DiceLimit(int, Enum):
    MIN_VALUE = 1
    MAX_VALUE_DICE = 6
    MAX_VALUE_DARTS = 6
    MAX_VALUE_BASKETBALL = 5
    MAX_VALUE_FOOTBALL = 5
    MAX_VALUE_SLOT_MACHINE = 64
    MAX_VALUE_BOWLING = 6


class _Dice(Element):
    value: int
    emoji: DiceEmoji

    def __init__(self, value: int) -> None:
        self.value = value

    @property
    def max_value(self) -> DiceLimit:
        return getattr(DiceLimit, f"MAX_VALUE_{self.emoji.name}")

    @property
    def min_value(self) -> DiceLimit:
        return DiceLimit.MIN_VALUE

    def __str__(self) -> str:
        return f"[${self.emoji.value}:value={self.value}]"


class Dice(_Dice):
    emoji: Final[DiceEmoji] = DiceEmoji.DICE


class Darts(_Dice):
    emoji: Final[DiceEmoji] = DiceEmoji.DARTS


class Basketball(_Dice):
    emoji: Final[DiceEmoji] = DiceEmoji.BASKETBALL


class Football(_Dice):
    emoji: Final[DiceEmoji] = DiceEmoji.FOOTBALL


class SlotMachine(_Dice):
    emoji: Final[DiceEmoji] = DiceEmoji.SLOT_MACHINE


class Bowling(_Dice):
    emoji: Final[DiceEmoji] = DiceEmoji.BOWLING


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
class _Entity(Text, Element):
    text: str
    type: MessageEntityType

    def __str__(self):
        return f"[${self.type.value}:text={self.text}]"


@dataclass
class Mention(Notice, _Entity):
    type: Final[MessageEntityType] = MessageEntityType.MENTION


@dataclass
class HashTag(_Entity):
    type: Final[MessageEntityType] = MessageEntityType.HASH_TAG


@dataclass
class Cashtag(_Entity):
    type: Final[MessageEntityType] = MessageEntityType.CASHTAG


@dataclass
class PhoneNumber(_Entity):
    type: Final[MessageEntityType] = MessageEntityType.PHONE_NUMBER


@dataclass
class BotCommand(_Entity):
    type: Final[MessageEntityType] = MessageEntityType.BOT_COMMAND


@dataclass
class Url(_Entity):
    type: Final[MessageEntityType] = MessageEntityType.URL


@dataclass
class Email(_Entity):
    type: Final[MessageEntityType] = MessageEntityType.EMAIL


@dataclass
class Bold(_Entity):
    type: Final[MessageEntityType] = MessageEntityType.BOLD


@dataclass
class Italic(_Entity):
    type: Final[MessageEntityType] = MessageEntityType.ITALIC


@dataclass
class Code(_Entity):
    type: Final[MessageEntityType] = MessageEntityType.CODE


@dataclass
class Pre(_Entity):
    language: str
    type: Final[MessageEntityType] = MessageEntityType.PRE


@dataclass
class TextLink(_Entity):
    url: str
    type: Final[MessageEntityType] = MessageEntityType.TEXT_LINK


@dataclass
class TextMention(_Entity):
    user: ...
    type: Final[MessageEntityType] = MessageEntityType.TEXT_MENTION


@dataclass
class Underline(_Entity):
    type: Final[MessageEntityType] = MessageEntityType.UNDERLINE


@dataclass
class Strikethrough(_Entity):
    type: Final[MessageEntityType] = MessageEntityType.STRIKETHROUGH


@dataclass
class Spoiler(_Entity):
    type: Final[MessageEntityType] = MessageEntityType.SPOILER


@dataclass
class CustomEmoji(_Entity):
    custom_emoji_id: str
    type: Final[MessageEntityType] = MessageEntityType.CUSTOM_EMOJI


class Invoice(Element):
    # To be implemented
    ...


class Game(Element):
    # To be implemented
    ...
