from __future__ import annotations
from typing import Any

from avilla.core.event import AvillaEvent
from avilla.core.ryanvk.collector.application import ApplicationCollector
from graia.amnesia.message import Element, MessageChain
from graia.ryanvk import Fn, PredicateOverload, TypeOverload, SimpleOverload

from avilla.standard.core.application.event import AvillaLifecycleEvent


class QQAPICapability((m := ApplicationCollector())._):
    @Fn.complex({SimpleOverload(): ["event_type"]})
    async def event_callback(self, event_type: str, raw_event: dict) -> AvillaEvent | AvillaLifecycleEvent | None:
        ...

    @Fn.complex({PredicateOverload(lambda _, raw: raw["type"]): ["raw_element"]})
    async def deserialize_element(self, raw_element: dict) -> Element:
        ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def serialize_element(self, element: Any) -> dict:
        ...

    async def deserialize(self, content: list[dict]):
        elements = []

        for raw_element in content:
            elements.append(await self.deserialize_element(raw_element))

        return MessageChain(elements)

    async def serialize(self, message: MessageChain):
        chain = []

        for element in message:
            chain.append(await self.serialize_element(element))

        return chain

    async def handle_event(self, event: dict):
        maybe_event = await self.event_callback(event)

        if maybe_event is not None:
            self.avilla.broadcast.postEvent(maybe_event)
