from dataclasses import dataclass
from typing import Literal, Optional, Union, List

from yarl import URL
from avilla.core.message import MessageChain
from avilla.core.selectors import entity as entity_selector
from avilla.core.elements import Image
from avilla.core.message import Element
from avilla.core.selectors import resource as resource_selector


class FlashImage(Image):
    pass


@dataclass
class Face(Element):
    id: str


class RPS(Element):
    pass


class Dice(Element):
    pass


class Shake(Element):
    pass


@dataclass
class Poke(Element):
    type: str
    id: str
    name: Optional[str] = None


@dataclass
class Anonymous(Element):
    ignore: bool


@dataclass
class Share(Element):
    url: URL
    title: str
    content: Optional[str] = None
    image: Optional[URL] = None


@dataclass
class Contact(Element):
    entity: entity_selector


@dataclass
class Location(Element):
    lat: float
    lon: float
    title: Optional[str] = None
    content: Optional[str] = None


@dataclass
class Music(Element):
    type: Union[Literal["qq"], Literal["163"], Literal["xm"], Literal["custom"]]
    id: Optional[str] = None
    url: Optional[URL] = None
    audio: Optional[URL] = None
    title: Optional[str] = None
    content: Optional[str] = None
    image: Optional[URL] = None


@dataclass
class Reply(Element):
    id: str


@dataclass
class Forward(Element):
    id: str


@dataclass
class Node(Element):
    id: Optional[str] = None
    user_id: Optional[str] = None
    nickname: Optional[str] = None
    content: Optional[MessageChain] = None


@dataclass
class XML(Element):
    data: str


@dataclass
class Json(Element):
    data: str
