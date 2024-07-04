from __future__ import annotations

from typing import Any, Literal

from graia.amnesia.message import Element, MessageChain

from avilla.core.event import AvillaEvent
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.ryanvk.overload.target import TargetOverload
from avilla.core.selector import Selector
from avilla.standard.core.application.event import AvillaLifecycleEvent
from graia.ryanvk import Fn, PredicateOverload, SimpleOverload, TypeOverload

from .utils import handle_text, remove_empty


class QQAPICapability((m := ApplicationCollector())._):
    @Fn.complex({SimpleOverload(): ["event_type"]})
    async def event_callback(self, event_type: str, raw_event: dict) -> AvillaEvent | AvillaLifecycleEvent | None:
        ...

    @Fn.complex({PredicateOverload(lambda _, raw: raw["type"]): ["raw_element"]})
    async def deserialize_element(self, raw_element: dict) -> Element:
        ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def serialize_element(self, element: Any) -> str | tuple[str, Any]:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def create_dms(self, target: Selector) -> Selector:
        """主动创建私聊会话，返回临时的 Guild"""
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def post_file(
        self,
        target: Selector,
        file_type: Literal[1, 2, 3, 4],
        url: str | None = None,
        srv_send_msg: bool = True,
        file_data: str | bytes | None = None,
    ) -> dict:
        """上传文件，返回文件信息"""
        ...

    async def deserialize(self, event: dict):
        elements = []

        if message_reference := event.get("message_reference"):
            elements.append(await self.deserialize_element({"type": "message_reference", **message_reference}))
        if event.get("mention_everyone", False):
            elements.append(await self.deserialize_element({"type": "mention_everyone"}))
        if "content" in event:
            for i in handle_text(event["content"]):
                elements.append(await self.deserialize_element(i))
        if attachments := event.get("attachments"):
            for i in attachments:
                elements.append(await self.deserialize_element({"type": "attachment", **i}))
        if embeds := event.get("embeds"):
            for i in embeds:
                elements.append(await self.deserialize_element({"type": "embed", **i}))
        if ark := event.get("ark"):
            elements.append(await self.deserialize_element({"type": "ark", **ark}))

        return MessageChain(elements)

    async def serialize(self, message: MessageChain):
        res = {}
        content = ""

        for element in message:
            elem = await self.serialize_element(element)
            if isinstance(elem, str):
                content += elem
            else:
                other = elem[1]
                res[elem[0]] = remove_empty(other) if isinstance(other, dict) else other
        if content:
            res["content"] = content
        return res

    async def handle_event(self, etype: str, event: dict):
        maybe_event = await self.event_callback(etype, event)

        if maybe_event is not None:
            self.avilla.broadcast.postEvent(maybe_event)
