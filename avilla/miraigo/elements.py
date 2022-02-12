from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional, Union, overload
from urllib.parse import urldefrag

from avilla.core.selectors import resource as resource_selector
from avilla.core.elements import Image
from avilla.core.message import Element, MessageChain
from avilla.core.selectors import entity as entity_selector
from avilla.onebot.elements import Reply, Music
from yarl import URL


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
