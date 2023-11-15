from __future__ import annotations

from typing import Any

from graia.amnesia.message import Element, MessageChain
from satori.element import Element as SatoriElement
from satori.model import Event

from avilla.core.event import AvillaEvent
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.standard.core.application.event import AvillaLifecycleEvent
from graia.ryanvk import Fn, PredicateOverload, TypeOverload


class SatoriCapability((m := ApplicationCollector())._):
    @Fn.complex({PredicateOverload(lambda _, raw: raw.type): ["raw_event"]})
    async def event_callback(self, raw_event: Event) -> AvillaEvent | AvillaLifecycleEvent | None:
        ...

    @Fn.complex({TypeOverload(): ["raw_element"]})
    async def deserialize_element(self, raw_element: Any) -> Element:
        ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def serialize_element(self, element: Any) -> str:
        ...

    async def deserialize(self, content: list[SatoriElement]):
        elements = []

        for raw_element in content:
            elements.append(await self.deserialize_element(raw_element))

        return MessageChain(elements)

    async def serialize(self, message: MessageChain):
        chain = []

        for element in message:
            chain.append(await self.serialize_element(element))

        return "".join(chain)

    async def handle_event(self, event: Event):
        maybe_event = await self.event_callback(event)

        if maybe_event is not None:
            self.avilla.event_record(maybe_event)
            self.avilla.broadcast.postEvent(maybe_event)
