from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from graia.amnesia.message.element import Element

from avilla.core.elements import Picture as CorePicture
from avilla.core.elements import Video as CoreVideo
from avilla.core.resource import LocalFileResource, Resource
from avilla.standard.telegram.constants import DiceEmoji, DiceLimit


class Picture(CorePicture):
    has_spoiler: bool

    def __init__(self, resource: Resource[bytes] | Resource[str] | Path | str, has_spoiler: bool = False):
        super().__init__(resource)
        self.has_spoiler = has_spoiler

    def __repr__(self):
        return f"[$Picture:resource={self.resource.to_selector()};has_spoiler={self.has_spoiler}]"


class Video(CoreVideo):
    has_spoiler: bool

    def __init__(self, resource: Resource[bytes] | Path | str, has_spoiler: bool = False):
        super().__init__(resource)
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
    vcard: str | None = None

    def __str__(self) -> str:
        return "[$Contact]"


@dataclass
class Location(Element):
    latitude: float
    longitude: float

    def __str__(self) -> str:
        return "[$Location]"


class Sticker(Element):
    resource: Resource[bytes] | Path | str
    width: int
    height: int
    is_animated: bool
    is_video: bool

    def __init__(
        self,
        resource: Resource[bytes] | Path | str,
        width: int = -1,
        height: int = -1,
        is_animated: bool = None,
        is_video: bool = None,
    ):
        if isinstance(resource, Path):
            resource = LocalFileResource(resource)
        elif isinstance(resource, str):
            resource = LocalFileResource(Path(resource))
        self.resource = resource
        self.width = width
        self.height = height
        self.is_animated = is_animated
        self.is_video = is_video

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


class Invoice(Element):
    # To be implemented
    ...


class Game(Element):
    # To be implemented
    ...
