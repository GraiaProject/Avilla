from __future__ import annotations

from typing import Any

from graia.amnesia.message import Element, MessageChain

from avilla.core.elements import Reference
from avilla.core.event import AvillaEvent
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.standard.core.application.event import AvillaLifecycleEvent
from graia.ryanvk import Fn, PredicateOverload, SimpleOverload, TypeOverload


class TelegramCapability((m := ApplicationCollector())._):
    @Fn.complex({SimpleOverload(): ["event_type"]})
    async def event_callback(self, event_type: str, raw_event: dict) -> AvillaEvent | AvillaLifecycleEvent | None: ...

    @Fn.complex({PredicateOverload(lambda _, raw: list(raw.keys())[-1]): ["raw_element"]})
    async def deserialize_element(self, raw_element: dict) -> list[Element]: ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def serialize_element(self, element: Any) -> dict: ...

    async def deserialize(self, raw: dict):
        ignored_keys: set[str] = {
            "has_media_spoiler",
            "link_preview_options",
            "has_protected_content",
            "is_topic_message",
            "is_automatic_forward",
        }
        return MessageChain(await self.deserialize_element({k: v for k, v in raw.items() if k not in ignored_keys}))

    async def serialize(self, message: MessageChain):
        ignored_elements: set[type[Element]] = {Reference}
        result = [await self.serialize_element(element) for element in message if type(element) not in ignored_elements]
        return [element for element in result if element]

    async def handle_event(self, event_type: str, payload: dict):
        maybe_event = await self.event_callback(event_type, payload)

        if maybe_event is not None:
            self.avilla.event_record(maybe_event)
            self.avilla.broadcast.postEvent(maybe_event)
