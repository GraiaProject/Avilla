from __future__ import annotations

from typing import Any, Protocol, TypeVar

from flywheel import (
    Fn,
    FnCompose,
    FnRecord,
    OverloadRecorder,
    SimpleOverload,
    TypeOverload,
)
from graia.amnesia.message import Element as GraiaElement
from graia.amnesia.message import MessageChain
from satori.element import Element as SatoriElement
from satori.element import transform
from satori.model import Event as SatoriEvent
from satori.parser import parse

from avilla.core.event import AvillaEvent
from avilla.standard.core.application.event import AvillaLifecycleEvent

SE = TypeVar("SE", bound=SatoriElement, contravariant=True)
GE = TypeVar("GE", bound=GraiaElement, contravariant=True)
SV = TypeVar("SV", bound=SatoriEvent, contravariant=True)


class SatoriCapability:
    @Fn.declare
    class event_callback(FnCompose):
        raw_event = SimpleOverload("raw_event")

        async def call(self, record: FnRecord, event: SatoriEvent):
            entities = self.load(self.raw_event.dig(record, event.type))
            return await entities.first(event=event)

        class shapecall(Protocol[SV]):
            async def __call__(self, event: SV) -> AvillaEvent | AvillaLifecycleEvent | list[Any]: ...

        def collect(self, recorder: OverloadRecorder[shapecall], raw_event: str):
            recorder.use(self.raw_event, raw_event)

    @Fn.declare
    class deserialize_element(FnCompose):
        type = TypeOverload("type")

        async def call(self, record: FnRecord, element: SatoriElement):
            entities = self.load(self.type.dig(record, element))
            return await entities.first(element=element)

        class shapecall(Protocol[SE]):
            async def __call__(self, element: SE) -> GraiaElement: ...

        def collect(self, recorder: OverloadRecorder[shapecall[SE]], element: type[SE]):
            recorder.use(self.type, element)

    @Fn.declare
    class serialize_element(FnCompose):
        type = TypeOverload("type")

        async def call(self, record: FnRecord, element: GraiaElement):
            entities = self.load(self.type.dig(record, element))
            return await entities.first(element=element)

        class shapecall(Protocol[GE]):
            async def __call__(self, element: GE) -> str: ...

        def collect(self, recorder: OverloadRecorder[shapecall[GE]], element: type[GE]):
            recorder.use(self.type, element)

    @staticmethod
    async def deserialize(content: str):
        elements = []

        for raw_element in transform(parse(content)):
            elements.append(await SatoriCapability.deserialize_element(raw_element))

        return MessageChain(elements)

    @staticmethod
    async def serialize(message: MessageChain):
        chain = []

        for element in message:
            chain.append(await SatoriCapability.serialize_element(element))

        return "".join(chain)
