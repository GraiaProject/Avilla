from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from graia.amnesia.message.element import Element

from avilla.core.elements import Audio as CoreAudio
from avilla.core.elements import Picture

# from avilla.core.elements import Video as CoreVideo
from avilla.standard.telegram.constants import DiceEmoji, DiceLimit
from avilla.standard.telegram.resource import TelegramResource


# region File Elements
class PhotoSize(Picture):
    resource: TelegramResource[bytes]
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


class Audio(CoreAudio, _ThumbedMedium):
    resource: TelegramResource[bytes]
    duration: int
    performer: str | None = None
    title: str | None = None
    file_name: str | None = None
    mime_type: str | None = None

    def __init__(
        self,
        resource: TelegramResource[bytes],
        duration: int,
        thumbnail: PhotoSize | None = None,
        performer: str | None = None,
        title: str | None = None,
    ):
        super().__init__(resource, duration)
        self.thumbnail = thumbnail
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


@dataclass
class Location(Element):
    longitude: float
    latitude: float
    horizontal_accuracy: float | None = None
    live_period: int | None = None
    heading: int | None = None
    proximity_alert_radius: int | None = None

    def __str__(self) -> str:
        return f"[$Location]"

    def __repr__(self) -> str:
        return f"[$Location:longitude={self.longitude};latitude={self.latitude}]"


class Sticker(_ThumbedMedium):
    width: int
    height: int
    is_animated: bool
    is_video: bool
    type: str
    emoji: str | None = None
    set_name: str | None = None
    mask_position: dict | None = None
    premium_animation: ... | None = None
    custom_emoji_id: str | None = None
    needs_repainting: bool | None = None

    def __init__(
        self,
        file_id: str,
        file_unique_id: str,
        width: int,
        height: int,
        is_animated: bool,
        is_video: bool,
        type: str,
        file_size: int | None = None,
        thumbnail: PhotoSize | None = None,
        emoji: str | None = None,
        set_name: str | None = None,
        mask_position: dict | None = None,
        premium_animation: ... | None = None,
        custom_emoji_id: str | None = None,
        needs_repainting: bool | None = None,
    ):
        super().__init__(file_id, file_unique_id, file_size, thumbnail)
        self.width = width
        self.height = height
        self.is_animated = is_animated
        self.is_video = is_video
        self.type = type
        self.emoji = emoji
        self.set_name = set_name
        self.mask_position = mask_position
        self.premium_animation = premium_animation
        self.custom_emoji_id = custom_emoji_id
        self.needs_repainting = needs_repainting

    def __str__(self) -> str:
        return f"[$Sticker:file_id={self.file_id}]"


@dataclass
class Venue(Element):
    location: Location
    title: str
    address: str
    foursquare_id: str | None = None
    foursquare_type: str | None = None
    google_place_id: str | None = None
    google_place_type: str | None = None

    def __str__(self) -> str:
        return f"[$Venue]"

    def __repr__(self) -> str:
        return f"[$Venue:location={self.location};title={self.title};address={self.address}]"


class Video(_ThumbedMedium):
    width: int
    height: int
    duration: int
    mime_type: str | None = None
    file_name: str | None = None

    def __init__(
        self,
        file_id: str,
        file_unique_id: str,
        width: int,
        height: int,
        duration: int,
        file_size: int | None = None,
        thumbnail: PhotoSize | None = None,
        mime_type: str | None = None,
        file_name: str | None = None,
    ):
        super().__init__(file_id, file_unique_id, file_size, thumbnail)
        self.width = width
        self.height = height
        self.duration = duration
        self.mime_type = mime_type
        self.file_name = file_name

    def __str__(self) -> str:
        return f"[$Video:file_id={self.file_id}]"


class VideoNote(_ThumbedMedium):
    length: int
    duration: int
    file_name: str | None = None
    mime_type: str | None = None

    def __init__(
        self,
        file_id: str,
        file_unique_id: str,
        length: int,
        duration: int,
        file_size: int | None = None,
        thumbnail: PhotoSize | None = None,
        file_name: str | None = None,
        mime_type: str | None = None,
    ):
        super().__init__(file_id, file_unique_id, file_size, thumbnail)
        self.length = length
        self.duration = duration
        self.file_name = file_name
        self.mime_type = mime_type

    def __str__(self) -> str:
        return f"[$VideoNote:file_id={self.file_id}]"


class Voice(_Medium):
    duration: int
    mime_type: str | None = None
    file_name: str | None = None

    def __init__(
        self,
        file_id: str,
        file_unique_id: str,
        duration: int,
        file_size: int | None = None,
        file_name: str | None = None,
        mime_type: str | None = None,
    ):
        super().__init__(file_id, file_unique_id, file_size)
        self.duration = duration
        self.file_name = file_name
        self.mime_type = mime_type

    def __str__(self) -> str:
        return f"[$Voice:file_id={self.file_id}]"


# endregion


# region Non-typical Elements
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


class Story(Element):
    """Currently holds no information."""


# endregion
