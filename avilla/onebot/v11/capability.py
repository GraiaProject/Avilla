from __future__ import annotations

from typing import Any, Protocol, TypeVar

from flywheel.globals import INSTANCE_CONTEXT_VAR
from graia.amnesia.message import Element, MessageChain

from avilla.core.event import AvillaEvent
from flywheel import Fn, FnCompose, OverloadRecorder, FnRecord, SimpleOverload, TypeOverload
from avilla.core.application import Avilla
from avilla.standard.core.application import AvillaLifecycleEvent

El = TypeVar("El", bound=Element)
El_co = TypeVar("El_co", bound=Element, covariant=True)
El_contra = TypeVar("El_contra", bound=Element, contravariant=True)

SPECIAL_POST_TYPE = {"message_sent": "message"}


def onebot11_event_type(raw: dict) -> str:
    return (
        f"{(post := raw['post_type'])}."
        f"{raw.get(f'{SPECIAL_POST_TYPE.get(post, post)}_type', '_')}"
        f"{f'.{sub}' if (sub:=raw.get('sub_type')) else ''}"
    )


class OneBot11Capability:
    @Fn.declare
    class event_callback(FnCompose):
        event_type = SimpleOverload("raw_event")

        async def call(self, record: FnRecord, raw_event: dict):
            entities = self.load(self.event_type.dig(record, onebot11_event_type(raw_event)))
            return await entities.first(raw_event=raw_event)
        
        class shapecall(Protocol):
            async def __call__(self, raw_event: dict) -> AvillaEvent | AvillaLifecycleEvent:
                ...
        
        def collect(self, recorder: OverloadRecorder[shapecall], event: str):
            recorder.use(self.event_type, event)

    @Fn.declare
    class serialize_element(FnCompose):
        element = TypeOverload("element")

        async def call(self, record: FnRecord, element: Element):
            entities = self.load(self.element.dig(record, element))
            return await entities.first(element=element)

        class shapecall(Protocol[El_contra]):
            async def __call__(self, element: El_contra) -> dict:
                ...

        def collect(self, recorder: OverloadRecorder[shapecall[El]], element_type: type[El]):
            recorder.use(self.element, element_type)

    @Fn.declare
    class deserialize_element(FnCompose):
        element = SimpleOverload("element")

        async def call(self, record: FnRecord, element: dict):
            entities = self.load(self.element.dig(record, element['type']))
            return await entities.first(element=element)

        class shapecall(Protocol):
            async def __call__(self, element: dict) -> Element:
                ...

        def collect(self, recorder: OverloadRecorder[shapecall], element_type: str):
            recorder.use(self.element, element_type)

    @staticmethod
    async def deserialize_chain(chain: list[dict]):
        elements = []

        for raw_element in chain:
            elements.append(await OneBot11Capability.deserialize_element(raw_element))

        return MessageChain(elements)

    @staticmethod
    async def serialize_chain(chain: MessageChain):
        elements = []

        for element in chain:
            elements.append(await OneBot11Capability.serialize_element(element))

        return elements

    @staticmethod
    async def handle_event(event: dict):
        maybe_event = await OneBot11Capability.event_callback(event)

        avilla = INSTANCE_CONTEXT_VAR.get().instances[Avilla]
        if maybe_event is not None:
            avilla.event_record(maybe_event)
            avilla.broadcast.postEvent(maybe_event)
