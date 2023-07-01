from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, Generic, TypeVar

from avilla.core._vendor.dataclasses import dataclass

if TYPE_CHECKING:
    from avilla.core.ryanvk.collector.protocol import (
        ProtocolBasedPerformTemplate,
        ProtocolCollector,
    )
    from graia.amnesia.message.element import Element

PBPT = TypeVar("PBPT", bound="ProtocolBasedPerformTemplate", contravariant=True)
E = TypeVar("E", bound="Element")


@dataclass(unsafe_hash=True)
class MessageSerializeSign(Generic[E]):
    element_type: type[Element]


class OneBot11MessageSerialize:
    @staticmethod
    def collect(collector: ProtocolCollector, element_type: type[E]):
        def receiver(entity: Callable[[PBPT, E], Awaitable[dict]]):
            collector.artifacts[MessageSerializeSign(element_type)] = (collector, entity)
            return entity

        return receiver
