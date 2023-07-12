from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, TypeVar

from avilla.core._vendor.dataclasses import dataclass

if TYPE_CHECKING:
    from avilla.core.event import AvillaEvent
    from avilla.standard.core.account.event import AvillaLifecycleEvent

    from ..collector.base import BaseCollector, PerformTemplate

M = TypeVar("M", bound="PerformTemplate", contravariant=True)


@dataclass(unsafe_hash=True)
class EventParserSign:
    event_type: str


class EventParse:
    @classmethod
    def collect(cls, collector: BaseCollector, event_type: str):
        def receiver(entity: Callable[[M, dict], Awaitable[AvillaEvent | AvillaLifecycleEvent | None]]):
            collector.artifacts[EventParserSign(event_type)] = (collector, entity)
            return entity

        return receiver
