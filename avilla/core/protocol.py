from __future__ import annotations

from contextlib import nullcontext
from functools import cached_property
from typing import TYPE_CHECKING, Any

from typing_extensions import Self
from flywheel import CollectContext

from avilla.core.globals import AVILLA_CONTEXT_VAR, CONTEXT_CONTEXT_VAR, PROTOCOL_CONTEXT_VAR
from avilla.core.event import AvillaEvent

if TYPE_CHECKING:
    from avilla.core.application import Avilla
    from avilla.core.context import Context


class ProtocolConfig: ...


class BaseProtocol:
    avilla: Avilla

    @cached_property
    def artifacts(self):
        with CollectContext().collect_scope() as collect_context:
            ...

        return collect_context

    def ensure(self, avilla: Avilla) -> Any: ...

    def configure(self, config: ProtocolConfig) -> Self: ...

    def post_event(self, event: AvillaEvent, context: Context | None = None):
        with (
            AVILLA_CONTEXT_VAR.use(self.avilla),
            PROTOCOL_CONTEXT_VAR.use(self),
            CONTEXT_CONTEXT_VAR.use(context) if context is not None else nullcontext(),
        ):
            self.avilla.event_record(event)
            return self.avilla.broadcast.postEvent(event)
