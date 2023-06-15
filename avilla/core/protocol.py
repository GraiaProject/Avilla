from __future__ import annotations

from contextlib import nullcontext
from typing import TYPE_CHECKING, Any, ClassVar

from avilla.core._runtime import cx_avilla, cx_context, cx_protocol
from avilla.core.event import AvillaEvent
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.ryanvk import processing_protocol
from avilla.core.ryanvk.common.isolate import Isolate

if TYPE_CHECKING:
    from avilla.core.application import Avilla
    from avilla.core.context import Context


class BaseProtocol:
    avilla: Avilla
    platform: ClassVar[Platform]

    isolate: ClassVar[Isolate]

    def __init_subclass__(cls) -> None:
        cls.isolate = Isolate()
        token = processing_protocol.set(cls)
        try:
            cls.__init_isolate__()
        finally:
            processing_protocol.reset(token)

    @classmethod
    def __init_isolate__(cls):
        ...

    @property
    def land(self):
        return self.platform[Land]

    @property
    def abstract(self):
        return self.platform[Abstract]

    def ensure(self, avilla: Avilla) -> Any:
        ...

    """
    def get_accounts(self, selector: Selector | None = None) -> list[AbstractAccount]:
        return self.avilla.get_accounts(selector=selector, land=self.platform[Land])

    def get_account(self, selector: Selector) -> AbstractAccount | None:
        return self.avilla.get_account(selector=selector, land=self.platform[Land])
    """

    def post_event(self, event: AvillaEvent, context: Context | None = None):
        with cx_avilla.use(self.avilla), cx_protocol.use(self), (
            cx_context.use(context) if context is not None else nullcontext()
        ):
            return self.avilla.broadcast.postEvent(event)
