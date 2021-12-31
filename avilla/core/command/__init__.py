from dataclasses import dataclass
from typing import Any, Callable, Dict, Type, Union

from graia.broadcast import Broadcast

from avilla.core.message import MessageChain
from avilla.core.utilles.selector import Selector

EllipsisType = type(Ellipsis)


class ParamDesc:
    ...


@dataclass
class Slot(ParamDesc):
    placeholder: Union[str, int, EllipsisType]
    type: Type = MessageChain


@dataclass
class Arg(ParamDesc):
    pattern: str
    type: Type
    placeholder_handler: Callable[[Dict[Union[str, int], Any]], Any] = lambda x: x


class Commander:
    broadcast: Broadcast

    def __init__(self, broadcast: Broadcast):
        self.broadcast = broadcast
