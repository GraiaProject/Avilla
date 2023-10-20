from __future__ import annotations

from typing import Any, TypeVar, AnyStr

from nonechat.info import Event as ConsoleEvent
from nonechat.message import Element as ConsoleElement

from avilla.core.event import AvillaEvent
from graia.amnesia.message import Element as GraiaElement
from graia.ryanvk import Capability, Fn, TypeOverload

CE = TypeVar("CE", bound=ConsoleElement)
GE = TypeVar("GE", bound=GraiaElement)
CV = TypeVar("CV", bound=ConsoleEvent)


class ConsoleCapability(Capability):
    @Fn.complex({TypeOverload(): ["event"]})
    async def event_callback(self, event: Any) -> AvillaEvent:
        ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def deserialize_element(self, element: Any) -> GraiaElement:
        ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def serialize_element(self, element: Any) -> ConsoleElement:
        ...
