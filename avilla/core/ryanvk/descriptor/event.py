from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Awaitable, Callable, Generic

from typing_extensions import TypeVar

from graia.ryanvk import BaseCollector, BasePerform, RecordTwin

if TYPE_CHECKING:
    from avilla.core.event import AvillaEvent
    from avilla.standard.core.account.event import AvillaLifecycleEvent

M = TypeVar("M", bound="BasePerform", contravariant=True)
VnEventRaw = TypeVar("VnEventRaw", default=dict)


@dataclass(unsafe_hash=True)
class EventParserSign:
    event_type: str


class EventParse(Generic[VnEventRaw]):
    @classmethod
    def collect(cls, collector: BaseCollector, event_type: str):
        def receiver(entity: Callable[[M, VnEventRaw], Awaitable[AvillaEvent | AvillaLifecycleEvent | None]]):
            collector.artifacts[EventParserSign(event_type)] = RecordTwin(collector, entity)
            return entity

        return receiver
