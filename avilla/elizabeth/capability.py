from __future__ import annotations

from typing import TYPE_CHECKING

from graia.amnesia.message import Element, MessageChain

from avilla.core.event import AvillaEvent
from avilla.core.ryanvk.collector.application import ApplicationCollector
from graia.ryanvk import Fn, PredicateOverload, TypeOverload

if TYPE_CHECKING:
    pass


class ElizabethCapability((m := ApplicationCollector())._):
    @Fn.complex({PredicateOverload(lambda _, raw: raw["type"]): ["event"]})
    async def event_callback(self, event: dict) -> AvillaEvent | None:
        ...

    @Fn.complex({PredicateOverload(lambda _, raw: raw["type"]): ["element"]})
    async def deserialize_element(self, element: dict) -> Element:  # type: ignore
        ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def serialize_element(self, element: Element) -> dict:  # type: ignore
        ...

    async def deserialize_chain(self, chain: list[dict]):
        elements = []

        for raw_element in chain:
            elements.append(await self.deserialize_element(raw_element))

        return MessageChain(elements)

    async def handle_event(self, event: dict):
        maybe_event = await self.event_callback(event)

        if maybe_event is not None:
            self.avilla.broadcast.postEvent(maybe_event)
