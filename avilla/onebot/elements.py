from dataclasses import dataclass

from yarl import URL

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
    type:str
    id: str
    name: str
class Anonymous(Element):
    ignore: bool
@dataclass
class Reply(Element):
    id: str
