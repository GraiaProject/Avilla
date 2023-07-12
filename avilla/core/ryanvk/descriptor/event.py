from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, TypeVar

from avilla.core._vendor.dataclasses import dataclass

if TYPE_CHECKING:
    from avilla.core.event import AvillaEvent
    from avilla.standard.core.account.event import AvillaLifecycleEvent

    from ....onebot.v11.collector.connection import (
        ConnectionBasedPerformTemplate,
        ConnectionCollector,
    )

M = TypeVar("M", bound="ConnectionBasedPerformTemplate", contravariant=True)


@dataclass(unsafe_hash=True)
class EventParserSign:
    event_type: str


class OneBot11EventParse:
    @classmethod
    def collect(cls, collector: ConnectionCollector, event_type: str):
        def receiver(entity: Callable[[M, dict], Awaitable[AvillaEvent | AvillaLifecycleEvent | None]]):
            collector.artifacts[EventParserSign(event_type)] = (collector, entity)
            return entity

        return receiver
