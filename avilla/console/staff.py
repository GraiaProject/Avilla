from __future__ import annotations

from typing import Any, Callable, Awaitable

from avilla.core.ryanvk.staff import Staff
from avilla.core.ryanvk.runner import use_record
from avilla.core.ryanvk.descriptor.event import EventParserSign
from avilla.core.ryanvk.descriptor.message.deserialize import MessageDeserializeSign
from avilla.core.ryanvk.descriptor.message.serialize import MessageSerializeSign
from avilla.core.event import AvillaEvent
from graia.amnesia.message import MessageChain
from graia.amnesia.message.element import Element
from avilla.console.message import ConsoleMessage
from avilla.console.frontend.info import Event as ConsoleEvent

class ConsoleStaff(Staff):
    async def parse_event(
        self,
        event_type: str,
        data: ConsoleEvent,
    ) -> AvillaEvent | None:
        sign = EventParserSign(event_type)
        if sign not in self.artifacts:
            return

        record: tuple[Any, Callable[[Any, ConsoleEvent], Awaitable[AvillaEvent | None]]] = self.artifacts[sign]

        async with use_record(self.components, record) as entity:
            return await entity(data)

    async def serialize_message(self, message: MessageChain) -> ConsoleMessage:
        result: list[Element] = []
        for element in message.content:
            element_type = type(element)
            sign = MessageSerializeSign(element_type)
            if sign not in self.artifacts:
                raise NotImplementedError(f"Element {element_type} serialize is not supported")

            async with use_record(self.components, self.artifacts[sign]) as entity:
                result.append(await entity(element))
        return ConsoleMessage(result)

    async def deserialize_message(self, raw_elements: ConsoleMessage) -> MessageChain:
        result: list[Element] = []
        for raw_element in raw_elements:
            element_type = raw_element.__class__.__name__
            sign = MessageDeserializeSign(element_type)
            if sign not in self.artifacts:
                raise NotImplementedError(f"Element {element_type} descrialize is not supported")

            async with use_record(self.components, self.artifacts[sign]) as entity:
                result.append(await entity(raw_element))
        return MessageChain(result)
