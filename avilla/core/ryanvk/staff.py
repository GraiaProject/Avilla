from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, ChainMap, TypeVar
from .runner import use_record
from .descriptor.event import EventParserSign
from .descriptor.message.serialize import MessageSerializeSign
from .descriptor.message.deserialize import MessageDeserializeSign
from .descriptor.fetch import FetchImplement
from ..utilles import identity

if TYPE_CHECKING:
    from .protocol import SupportsArtifacts, SupportsStaff
    from avilla.core.event import AvillaEvent
    from graia.amnesia.message import MessageChain, Element
    from avilla.core.resource import Resource


T = TypeVar("T")


class Staff:
    components: dict[str, SupportsArtifacts]
    artifacts: ChainMap[Any, Any]

    def __init__(self, focus: SupportsStaff) -> None:
        self.components = focus.get_staff_components()
        self.artifacts = focus.get_staff_artifacts()

    async def parse_event(
        self,
        event_type: str,
        data: dict,
    ) -> AvillaEvent | None:
        sign = EventParserSign(event_type)
        if sign not in self.artifacts:
            raise NotImplementedError(f"Event {event_type} parse is not supported: {data}")

        record: tuple[Any, Callable[[Any, dict], Awaitable[AvillaEvent | None]]] = self.artifacts[sign]

        async with use_record(self.components, record) as entity:
            return await entity(data)

    async def serialize_message(self, message: MessageChain) -> list[dict]:
        result: list[dict] = []
        for element in message.content:
            element_type = type(element)
            sign = MessageSerializeSign(element_type)
            if sign not in self.artifacts:
                raise NotImplementedError(f"Element {element_type} serialize is not supported")

            async with use_record(self.components, self.artifacts[sign]) as entity:
                result.append(await entity(element))
        return result

    async def deserialize_message(self, raw_elements: list[dict]) -> MessageChain:
        result: list[Element] = []
        for raw_element in raw_elements:
            element_type = raw_element["type"]
            sign = MessageDeserializeSign(element_type)
            if sign not in self.artifacts:
                raise NotImplementedError(f"Element {element_type} descrialize is not supported")

            async with use_record(self.components, self.artifacts[sign]) as entity:
                result.append(await entity(raw_element))
        return MessageChain(result)

    async def fetch_resource(self, resource: Resource[T]) -> T:
        sign = FetchImplement(type(resource))
        if sign not in self.artifacts:
            raise NotImplementedError(f"Resource {identity(resource)} fetch is not supported")

        record: tuple[Any, Callable[[Any, Resource[T]], Awaitable[T]]] = self.artifacts[sign]
        async with use_record(self.components, record) as entity:
            return await entity(resource)
