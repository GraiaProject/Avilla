from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, TypeVar

from avilla.core._vendor.dataclasses import dataclass
from avilla.core.ryanvk.descriptor.event import EventParserSign

from avilla.console.frontend.info import Event as ConsoleEvent

if TYPE_CHECKING:
    from avilla.core.event import AvillaEvent
    from avilla.core.ryanvk.collector.base import BaseCollector, PerformTemplate
    from avilla.standard.core.account.event import AvillaLifecycleEvent

M = TypeVar("M", bound="PerformTemplate", contravariant=True)
CE = TypeVar("CE", bound=ConsoleEvent)


class ConsoleEventParse:
    @classmethod
    def collect(cls, collector: BaseCollector, event_sign: str, event_type: type[CE]):
        def receiver(
            entity: Callable[
                [M, CE], Awaitable[AvillaEvent | AvillaLifecycleEvent | None]
            ]
        ):
            collector.artifacts[EventParserSign(event_sign)] = (collector, entity)
            return entity

        return receiver
