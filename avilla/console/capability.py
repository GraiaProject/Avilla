from __future__ import annotations

from typing import Protocol, TypeVar

from graia.amnesia.message import Element as GraiaElement
from nonechat.info import Event as ConsoleEvent
from nonechat.message import Element as ConsoleElement

from avilla.core.event import AvillaEvent
from flywheel import TypeOverload, Fn, FnCompose, FnRecord, OverloadRecorder

CE = TypeVar("CE", bound=ConsoleElement, contravariant=True)
GE = TypeVar("GE", bound=GraiaElement, contravariant=True)
CV = TypeVar("CV", bound=ConsoleEvent, contravariant=True)


# NOTE: 全使用 global_collect 或是 scoped_collect.globals() 最好。

class ConsoleCapability:
    @Fn.declare
    class event_callback(FnCompose):
        type = TypeOverload("type")

        async def call(self, record: FnRecord, event: ConsoleEvent):
            from loguru import logger
            logger.info(event)
            entities = self.load(self.type.dig(record, event))
            return await entities.first(event=event)

        class shapecall(Protocol[CV]):
            async def __call__(self, event: CV) -> AvillaEvent: ...

        def collect(self, recorder: OverloadRecorder[shapecall[CV]], event: type[CV]):
            recorder.use(self.type, event)

    @Fn.declare
    class deserialize_element(FnCompose):
        type = TypeOverload("type")

        async def call(self, record: FnRecord, element: ConsoleElement):
            entities = self.load(self.type.dig(record, element))
            return await entities.first(element=element)

        class shapecall(Protocol[CE]):
            async def __call__(self, element: CE) -> GraiaElement: ...

        def collect(self, recorder: OverloadRecorder[shapecall[CE]], element: type[CE]):
            recorder.use(self.type, element)

    @Fn.declare
    class serialize_element(FnCompose):
        type = TypeOverload("type")

        async def call(self, record: FnRecord, element: GraiaElement):
            entities = self.load(self.type.dig(record, element))
            return await entities.first(element=element)

        class shapecall(Protocol[GE]):
            async def __call__(self, element: GE) -> ConsoleElement: ...

        def collect(self, recorder: OverloadRecorder[shapecall[GE]], element: type[GE]):
            recorder.use(self.type, element)
