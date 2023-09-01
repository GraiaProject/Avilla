from __future__ import annotations

from contextlib import nullcontext
from typing import TYPE_CHECKING, Any, ClassVar
from typing_extensions import Self

from avilla.core._runtime import cx_avilla, cx_context, cx_protocol
from avilla.core.event import AvillaEvent
from graia.ryanvk._runtime import processing_artifact_heap

if TYPE_CHECKING:
    from avilla.core.application import Avilla
    from avilla.core.context import Context

class ProtocolConfig:
    ...


class BaseProtocol:
    avilla: Avilla
    artifacts: ClassVar[dict[Any, Any]]

    def __init_subclass__(cls) -> None:
        cls.artifacts = {}

        token = processing_artifact_heap.set(cls.artifacts)
        try:
            cls.__init_isolate__()
        finally:
            processing_artifact_heap.reset(token)

    @classmethod
    def __init_isolate__(cls):
        ...

    def ensure(self, avilla: Avilla) -> Any:
        ...

    def configure(self, config: ProtocolConfig) -> Self:
        ...

    def post_event(self, event: AvillaEvent, context: Context | None = None):
        with cx_avilla.use(self.avilla), cx_protocol.use(self), (
            cx_context.use(context) if context is not None else nullcontext()
        ):
            return self.avilla.broadcast.postEvent(event)
