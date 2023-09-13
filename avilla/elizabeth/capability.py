from __future__ import annotations

from typing import Any

from avilla.core.event import AvillaEvent
from graia.amnesia.message import Element
from graia.ryanvk import Capability, Fn, TypeOverload



class ElizabethCapability(Capability):
    @Fn.complex({TypeOverload(): ["event"]})
    async def event_callback(self, event: dict) -> AvillaEvent:
        ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def deserialize_element(self, element: dict) -> Element:  # type: ignore
        ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def serialize_element(self, element: Element) -> dict:  # type: ignore
        ...
