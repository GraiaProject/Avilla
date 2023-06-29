from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypeVar

from avilla.core._vendor.dataclasses import dataclass

if TYPE_CHECKING:
    from avilla.core.event import AvillaEvent
    from avilla.core.ryanvk.collector.protocol import (
        ProtocolBasedPerformTemplate,
        ProtocolCollector,
    )

PBPT = TypeVar("PBPT", bound="ProtocolBasedPerformTemplate", contravariant=True)


class EventParser(Protocol):
    async def __call__(_, self: PBPT, data: dict) -> AvillaEvent:  # type: ignore
        ...


@dataclass
class EventParserSign:
    event_type: str


class OneBot11EventParse:
    @classmethod
    def collect(cls, collector: ProtocolCollector, event_type: str):
        def receiver(entity: EventParser):
            collector.artifacts[EventParserSign(event_type)] = (collector, entity)
            return entity

        return receiver
