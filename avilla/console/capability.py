from __future__ import annotations

from typing import NoReturn, TypeVar

from nonechat.info import Event as ConsoleEvent
from nonechat.message import Element as ConsoleElement

from avilla.core.event import AvillaEvent
from graia.amnesia.message import Element as GraiaElement
from graia.ryanvk import Capability, Fn, TypeOverload

CE = TypeVar("CE", bound=ConsoleElement)
GE = TypeVar("GE", bound=GraiaElement)
CV = TypeVar("CV", bound=ConsoleEvent)

GE_T = TypeVar("GE_T", bound=NoReturn, contravariant=True)


class ConsoleCapability(Capability):
    @Fn.complex({TypeOverload(): ["event"]})
    async def event_callback(self, event: CV) -> AvillaEvent:  # type: ignore
        ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def deserialize_element(self, element: CE) -> GraiaElement:  # type: ignore
        ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def serialize_element(self, element: GE) -> ConsoleElement:  # type: ignore
        ...
