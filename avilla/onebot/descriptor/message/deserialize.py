from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, TypeVar

from avilla.core._vendor.dataclasses import dataclass

if TYPE_CHECKING:
    from avilla.core.ryanvk.collector.protocol import (
        ProtocolBasedPerformTemplate,
        ProtocolCollector,
    )
    from graia.amnesia.message.element import Element

PBPT = TypeVar("PBPT", bound="ProtocolBasedPerformTemplate", contravariant=True)


@dataclass
class MessageDeserializeSign:
    element_type: str


class OneBot11MessageDeserialize:
    @classmethod
    def collect(cls, collector: ProtocolCollector, element_type: str):
        def receiver(entity: Callable[[PBPT, dict], Awaitable[Element]]):
            collector.artifacts[MessageDeserializeSign(element_type)] = (collector, entity)
            return entity

        return receiver
