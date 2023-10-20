from __future__ import annotations

from avilla.core.selector import Selector
from avilla.core.event import AvillaEvent
from avilla.core.ryanvk.overload.target import TargetOverload
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.standard.qq.elements import Forward
from graia.amnesia.message import Element, MessageChain
from graia.ryanvk import Fn, PredicateOverload, TypeOverload, SimpleOverload
from avilla.standard.core.application.event import AvillaLifecycleEvent

class RedCapability((m := ApplicationCollector())._):
    @Fn.complex({SimpleOverload(): ["event_type"]})
    async def event_callback(self, event_type: str, raw_event: dict) -> AvillaEvent | AvillaLifecycleEvent | None:
        ...

    @Fn.complex({PredicateOverload(lambda _, raw: raw["type"]): ["element"]})
    async def deserialize_element(self, element: dict) -> Element:  # type: ignore
        ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def serialize_element(self, element: Any) -> dict:  # type: ignore
        ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def forward_export(self, element: Any) -> dict:  # type: ignore
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def send_forward(self, target: Selector, forward: Forward) -> Selector:
        ...

    async def deserialize(self, elements: list[dict]):
        _elements = []

        for raw_element in elements:
            _elements.append(await self.deserialize_element(raw_element))

        return MessageChain(_elements)

    async def serialize(self, message: MessageChain):
        chain = []

        for element in message:
            chain.append(await self.serialize_element(element))

        return chain

    async def handle_event(self, event_type: str, payload: dict):
        maybe_event = await self.event_callback(event_type, payload)

        if maybe_event is not None:
            self.avilla.broadcast.postEvent(maybe_event)
