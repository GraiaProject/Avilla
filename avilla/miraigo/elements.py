from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional, Union, overload

from yarl import URL

from avilla.core.elements import Image, Video
from avilla.core.message import Element
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import resource as resource_selector
from avilla.onebot.elements import XML, Json, Music, Reply


class CardImage(Image):
    minwidth: int
    minheight: int
    maxwidth: int
    maxheight: int
    source_name: Optional[str]
    icon: Optional[URL]

    def __init__(
        self,
        source: Union[resource_selector, Path, str],
        minwidth: int = 400,
        minheight: int = 400,
        maxwidth: int = 500,
        maxheight: int = 1000,
        source_name: Optional[str] = None,
        icon: Optional[URL] = None,
    ):
        self.minwidth = minwidth
        self.minheight = minheight
        self.maxwidth = maxwidth
        self.maxheight = maxheight
        self.source_name = source_name
        self.icon = icon
        super().__init__(source)


class Image(Image):
    sub_type: Optional[str]

    def __init__(self, source: Union[resource_selector, Path, str], sub_type: Optional[str] = None):
        self.sub_type = sub_type
        super().__init__(source)


class FlashImage(Image):
    pass


class ShowImage(Image):
    id: Optional[str]

    def __init__(
        self,
        source: Union[resource_selector, Path, str],
        sub_type: Optional[str] = None,
        id: Optional[str] = None,
    ):
        self.id = id
        super().__init__(source, sub_type)


@dataclass
class Reply(Reply):
    id: Optional[str] = None
    text: Optional[str] = None
    qq: Optional[str] = None
    time: Optional[datetime] = None
    seq: Optional[str] = None
    if TYPE_CHECKING:

        @overload
        def __init__(self, id: str):
            ...

        @overload
        def __init__(self, *, text: str, qq: str, seq: str, time: Optional[datetime] = None):
            ...

        def __init__(self, *args, **kwargs):
            ...


class Music(Music):
    type: Literal["qq", "163", "custom"]
    sub_type: Literal["qq", "163", "migu", "kugou", "kuwo"]
    if TYPE_CHECKING:

        @overload
        def __init__(self, type: Literal["qq", "163"], id: str):
            ...

        @overload
        def __init__(
            self,
            type: Literal["custom"],
            *,
            sub_type: Literal["qq", "163", "migu", "kugou", "kuwo"],
            url: URL,
            audio: URL,
            title: str,
            content: Optional[str] = None,
            image: Optional[URL] = None,
        ):
            ...

        def __init__(self, *args, **kwargs):
            ...


@dataclass
class Redbag(Element):
    title: str


@dataclass
class Poke(Element):
    qq: entity_selector


class Video(Video):
    cover: resource_selector

    def __init__(self, source: resource_selector, cover: resource_selector):
        self.cover = cover
        super().__init__(source)


class XML(XML):
    resid: int

    def __init__(self, data: str, resid: int = 0):
        self.resid = resid
        super().__init__(data)


class Json(Json):
    resid: int

    def __init__(self, data: str, resid: int = 0):
        self.resid = resid
        super().__init__(data)


@dataclass
class TTS(Element):
    text: str
