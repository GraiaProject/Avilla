from __future__ import annotations

from typing import Any, TypeVar

from graia.amnesia.message import Element as GraiaElement
from nonechat.info import Event as ConsoleEvent
from nonechat.message import Element as ConsoleElement

from avilla.core.event import AvillaEvent
from avilla.core.ryanvk.collector.application import ApplicationCollector
from graia.ryanvk import Fn, TypeOverload

CE = TypeVar("CE", bound=ConsoleElement)
GE = TypeVar("GE", bound=GraiaElement)
CV = TypeVar("CV", bound=ConsoleEvent)


class ConsoleCapability((m := ApplicationCollector())._):
    @Fn.complex({TypeOverload(): ["event"]})
    async def event_callback(self, event: Any) -> AvillaEvent:
        ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def deserialize_element(self, element: Any) -> GraiaElement:
        ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def serialize_element(self, element: Any) -> ConsoleElement:
        ...
