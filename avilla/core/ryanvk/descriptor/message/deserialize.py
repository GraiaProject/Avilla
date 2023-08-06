from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Generic, TypeVar

if TYPE_CHECKING:
    from avilla.core.ryanvk.collector.base import BaseCollector
    from graia.amnesia.message.element import Element

T = TypeVar("T")


@dataclass(unsafe_hash=True)
class MessageDeserializeSign:
    element_type: str


class MessageDeserialize(Generic[T]):
    @classmethod
    def collect(cls: type[MessageDeserialize[T]], collector: BaseCollector, element_type: str):
        def receiver(entity: Callable[[Any, T], Awaitable[Element]]):
            collector.artifacts[MessageDeserializeSign(element_type)] = (collector, entity)
            return entity

        return receiver
