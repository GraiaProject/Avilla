from __future__ import annotations

from datetime import datetime
from typing import Any, TypedDict, cast

from avilla.core.ryanvk.staff import Staff
from avilla.core.ryanvk.runner import use_record
from avilla.core.ryanvk.descriptor.message.deserialize import MessageDeserializeSign
from graia.amnesia.message import MessageChain
from graia.amnesia.message.element import Element

class MessageDeserializeResult(TypedDict):
    content: MessageChain
    source: str
    time: datetime
    reply: str | None

class ElizabethStaff(Staff):

    async def deserialize_message(self, raw_elements: list[dict]):
        serialized: list[Element] = []
        result: dict[str, Any] = {
            "source": str(raw_elements[0]["id"]),
            "time": datetime.fromtimestamp(raw_elements[0]["time"]),
        }
        for raw_element in raw_elements[1:]:
            element_type = raw_element["type"]
            if element_type == "Quote":
                result["reply"] = str(raw_element["id"])
                continue
            sign = MessageDeserializeSign(element_type)
            if sign not in self.artifacts:
                raise NotImplementedError(f"Element {element_type} descrialize is not supported")

            async with use_record(self.components, self.artifacts[sign]) as entity:
                serialized.append(await entity(raw_element))
        result["content"] = MessageChain(serialized)
        return cast(MessageDeserializeResult, result)
