from __future__ import annotations

from collections import ChainMap
from typing import TYPE_CHECKING, Any

from avilla.core.elements import Element
from avilla.core.event import AvillaEvent
from avilla.core.ryanvk.descriptor.message.deserialize import MessageDeserializeSign
from graia.amnesia.message import MessageChain
from graia.ryanvk import RecordTwin, Staff

from .descriptor.endpoint import NoneEndpoint
from .descriptor.event import NoneEventTranslateSign
from .reference.event import Event
from .reference.message import Message

if TYPE_CHECKING:
    ...


class NoneBridgeStaff(Staff):
    async def deserialize_onebot_message(self, raw_elements: Message) -> MessageChain:
        result: list[Element] = []
        artifact_map = ChainMap(*self.artifact_collections)["onebot_message_parse"]

        for raw_element in raw_elements:
            element_type = raw_element.type
            sign = MessageDeserializeSign(element_type)
            if sign not in artifact_map:
                raise NotImplementedError(f"Element {element_type} descrialize is not supported: {raw_element}")

            record = artifact_map[sign]
            instance, entity = record.unwrap(self)
            result.append(await entity(instance, {"type": element_type, "data": raw_element.data}))

        return MessageChain(result)

    async def call_endpoint_api(self, endpoint: str, **kwargs) -> Any:
        record: RecordTwin | None = ChainMap(*self.artifact_collections).get(NoneEndpoint(endpoint))
        if record is None:
            raise NotImplementedError

        instance, entity = record.unwrap(self)
        return await entity(instance, **kwargs)

    async def translate_event(self, event: AvillaEvent) -> Event | None:
        record: RecordTwin | None = ChainMap(*self.artifact_collections).get(NoneEventTranslateSign(type(event)))
        if record is None:
            return

        instance, entity = record.unwrap(self)
        return await entity(instance, event)
