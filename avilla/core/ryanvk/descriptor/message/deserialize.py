from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, Generic, TypeVar, Any

from avilla.core._vendor.dataclasses import dataclass

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
