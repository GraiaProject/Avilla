from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

from graia.ryanvk.collector import BaseCollector
from graia.ryanvk.typing import RecordTwin

if TYPE_CHECKING:
    ...


@dataclass(eq=True, frozen=True)
class NoneEndpoint:
    name: str


class NoneEndpointFn:
    @classmethod
    def collect(cls, collector: BaseCollector, name: str):
        def wrapper(entity: Callable[..., Any]):
            collector.artifacts[NoneEndpoint(name)] = RecordTwin(collector, entity)
            return entity

        return wrapper
