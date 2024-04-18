from __future__ import annotations

from typing import Any

from graia.amnesia.message import Element, MessageChain

from avilla.core import Selector
from avilla.core.event import AvillaEvent
from avilla.core.ryanvk import TargetOverload
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.standard.core.application import AvillaLifecycleEvent
from avilla.standard.qq.elements import Forward
from graia.ryanvk import Fn, PredicateOverload, TypeOverload

SPECIAL_POST_TYPE = {"message_sent": "message"}


def onebot11_event_type(raw: dict) -> str:
    return (
        f"{(post := raw['post_type'])}."
        f"{raw.get(f'{SPECIAL_POST_TYPE.get(post, post)}_type', '_')}"
        f"{f'.{sub}' if (sub:=raw.get('sub_type')) else ''}"
    )


class OneBot11Capability((m := ApplicationCollector())._):
    @Fn.complex({PredicateOverload(lambda _, raw: onebot11_event_type(raw)): ["raw_event"]})
    async def event_callback(self, raw_event: dict) -> AvillaEvent | AvillaLifecycleEvent | None:
        ...

    @Fn.complex({PredicateOverload(lambda _, raw: raw["type"]): ["raw_element"]})
    async def deserialize_element(self, raw_element: dict) -> Element:  # type: ignore
        ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def serialize_element(self, element: Any) -> dict:  # type: ignore
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def send_forward_msg(self, target: Selector, forward: Forward) -> Selector:
        """发送合并转发消息"""
        ...

    async def deserialize_chain(self, chain: list[dict]):
        elements = []

        for raw_element in chain:
            elements.append(await self.deserialize_element(raw_element))

        return MessageChain(elements)

    async def serialize_chain(self, chain: MessageChain):
        elements = []

        for element in chain:
            elements.append(await self.serialize_element(element))

        return elements

    async def handle_event(self, event: dict):
        maybe_event = await self.event_callback(event)

        if maybe_event is not None:
            self.avilla.event_record(maybe_event)
            self.avilla.broadcast.postEvent(maybe_event)
