from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from graia.amnesia.message.element import Element

from avilla.core.elements import Picture
from avilla.standard.telegram.constants import DiceEmoji, DiceLimit
from avilla.standard.telegram.resource import TelegramResource


class PhotoSize(Picture):
    resource: TelegramResource
    width: int
    height: int

    def __init__(self, resource: TelegramResource, width: int, height: int):
        super().__init__(resource)
        self.width = width
        self.height = height

    def __str__(self) -> str:
        return f"[$PhotoSize]"

    def __repr__(self) -> str:
        return f"[$PhotoSize:file_id={self.resource.file_id};width={self.width};height={self.height}]"


@dataclass
class _Medium(Element):
    file_id: str
    file_unique_id: str
    file_size: int | None = None

    def __str__(self) -> str:
        return f"[$Medium]"

    def __repr__(self) -> str:
        return f"[$Medium:file_id={self.file_id}]"

    def __hash__(self):
        return hash(self.file_unique_id)

    def __eq__(self, other):
        return isinstance(other, _Medium) and self.file_unique_id == other.file_unique_id


@dataclass
class _ThumbedMedium(_Medium):
    thumbnail: PhotoSize | None = None

    def __str__(self):
        return f"[$ThumbedMedium]"

    def __repr__(self):
        return f"[$ThumbedMedium:file_id={self.file_id}]"


class Animation(_ThumbedMedium):
    width: int
    height: int
    duration: int
    file_name: str | None = None
    mime_type: str | None = None

    def __init__(
        self,
        file_id: str,
        file_unique_id: str,
        width: int,
        height: int,
        duration: int,
        file_size: int | None = None,
        thumbnail: PhotoSize | None = None,
    ):
        super().__init__(file_id, file_unique_id, file_size, thumbnail)
        self.width = width
        self.height = height
        self.duration = duration

    def __str__(self) -> str:
        return f"[$Animation:file_id={self.file_id}]"


class Audio(_ThumbedMedium):
    duration: int
    performer: str | None = None
    title: str | None = None
    file_name: str | None = None
    mime_type: str | None = None

    def __init__(
        self,
        file_id: str,
        file_unique_id: str,
        duration: int,
        file_size: int | None = None,
        thumbnail: PhotoSize | None = None,
        performer: str | None = None,
        title: str | None = None,
    ):
        super().__init__(file_id, file_unique_id, file_size, thumbnail)
        self.duration = duration
        self.performer = performer
        self.title = title

    def __str__(self) -> str:
        return f"[$Audio:file_id={self.file_id}]"


@dataclass
class Contact(Element):
    phone_number: str
    first_name: str
    last_name: str | None = None
    user_id: int | None = None
    vcard: str | None = None


@dataclass
class Document(_ThumbedMedium):
    file_name: str | None = None
    mime_type: str | None = None

    def __str__(self) -> str:
        return f"[$Document:file_id={self.file_id}]"


# <editor-fold desc="Dice Elements">
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
        return f"[$Dice:value={self.value};emoji={self.emoji}]"


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


# </editor-fold>


@dataclass
class ForceReply(Element):
    # Fun fact, I haven't used this before, nor do I know what it is. But it exists.

    selective: bool | None = None
    input_field_placeholder: str | None = None

    def __str__(self) -> str:
        return "[$ForceReply]"

    def __repr__(self) -> str:
        return f"[$ForceReply:selective={self.selective};input_field_placeholder={self.input_field_placeholder}]"


# TODO: Way More Elements...


class Story(Element):
    """Currently holds no information."""
