from __future__ import annotations

from avilla.core.event import AvillaEvent
from avilla.core.ryanvk.collector.application import ApplicationCollector
from graia.amnesia.message import Element, MessageChain
from graia.ryanvk import Fn, PredicateOverload, TypeOverload

from .utils import parse, Element as SatoriElement


class SatoriCapability((m := ApplicationCollector())._):
    @Fn.complex({PredicateOverload(lambda _, raw: raw["type"]): ["event"]})
    async def event_callback(self, event: dict) -> AvillaEvent | None:
        ...

    @Fn.complex({PredicateOverload(lambda _, raw: raw.type): ["element"]})
    async def deserialize_element(self, element: SatoriElement) -> Element:  # type: ignore
        ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def serialize_element(self, element: Element) -> str:  # type: ignore
        ...

    async def deserialize(self, content: str):
        elements = []

        for raw_element in parse(content):
            elements.append(await self.deserialize_element(raw_element))

        return MessageChain(elements)

    async def serialize(self, message: MessageChain):
        chain = []

        for element in message:
            chain.append(await self.serialize_element(element))

        return "".join(chain)

    async def handle_event(self, event: dict):
        maybe_event = await self.event_callback(event)

        if maybe_event is not None:
            self.avilla.broadcast.postEvent(maybe_event)
