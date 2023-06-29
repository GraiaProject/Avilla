from __future__ import annotations

from typing import TYPE_CHECKING, cast

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol

from .event.descriptor import EventParser, EventParserSign

if TYPE_CHECKING:
    from avilla.core.event import AvillaEvent
    from avilla.core.ryanvk.collector.protocol import ProtocolCollector

    from .account import OneBot11Account


class OneBot11Protocol(BaseProtocol):
    @classmethod
    def __init_isolate__(cls):
        ...

    def ensure(self, avilla: Avilla):
        ...

    async def parse_event(
        self,
        account: OneBot11Account,
        event_type: str,
        data: dict,
    ) -> AvillaEvent:
        collector, entity = cast(
            "tuple[ProtocolCollector[OneBot11Protocol, OneBot11Account], EventParser]",
            self.isolate.artifacts[EventParserSign(event_type)],
        )
        instance = collector.cls(self, account)
        return await entity(instance, data)
