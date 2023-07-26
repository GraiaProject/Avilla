from __future__ import annotations

from contextlib import nullcontext
from typing import TYPE_CHECKING, Any, ClassVar

from avilla.core._runtime import cx_avilla, cx_context, cx_protocol
from avilla.core.event import AvillaEvent
from avilla.core.ryanvk._runtime import ARTIFACT_COLLECTIONS, processing_isolate
from avilla.core.ryanvk.isolate import Isolate

if TYPE_CHECKING:
    from avilla.core.application import Avilla
    from avilla.core.context import Context


class BaseProtocol:
    avilla: Avilla
    isolate: ClassVar[Isolate]

    def __init_subclass__(cls) -> None:
        cls.isolate = Isolate()
        cls.isolate.artifacts = ARTIFACT_COLLECTIONS.setdefault(
            f"{cls.__module__}:{cls.__name__}", {"lookup_collections": [{}]}
        )

        token = processing_isolate.set(cls.isolate)
        try:
            cls.__init_isolate__()
        finally:
            processing_isolate.reset(token)

    @classmethod
    def __init_isolate__(cls):
        ...

    def ensure(self, avilla: Avilla) -> Any:
        ...

    def post_event(self, event: AvillaEvent, context: Context | None = None):
        with cx_avilla.use(self.avilla), cx_protocol.use(self), (
            cx_context.use(context) if context is not None else nullcontext()
        ):
            return self.avilla.broadcast.postEvent(event)
