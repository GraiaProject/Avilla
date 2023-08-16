from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Coroutine, TypeVar

from avilla.core.event import AvillaEvent
from graia.ryanvk.collector import BaseCollector
from graia.ryanvk.typing import RecordTwin

from ..reference.event import Event

if TYPE_CHECKING:
    ...

E = TypeVar("E", bound=AvillaEvent)


@dataclass(eq=True, frozen=True)
class NoneEventTranslateSign:
    event: type[AvillaEvent]


class NoneEventTranslate:
    @classmethod
    def collect(cls, collector: BaseCollector, event: type[E]):
        def wrapper(entity: Callable[[Any, E], Coroutine[None, None, Event | None]]):
            collector.artifacts[NoneEventTranslateSign(event)] = RecordTwin(collector, entity)
            return entity

        return wrapper
