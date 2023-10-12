from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import TYPE_CHECKING, AsyncIterator
from typing_extensions import Self

from loguru import logger

from avilla.core.selector import Selector
from avilla.core.ryanvk.staff import Staff
from avilla.satori.account import SatoriAccount
from avilla.satori.capability import SatoriCapability

if TYPE_CHECKING:
    from avilla.satori.protocol import SatoriProtocol


class SatoriNetworking:
    protocol: SatoriProtocol
    accounts: dict[str, SatoriAccount]
    close_signal: asyncio.Event
    sequence: int

    def __init__(self, protocol: SatoriProtocol):
        super().__init__()
        self.protocol = protocol
        self.accounts = {}
        self.close_signal = asyncio.Event()
        self.sequence = -1

    def get_staff_components(self):
        return {"connection": self, "protocol": self.protocol, "avilla": self.protocol.avilla}

    def get_staff_artifacts(self):
        return [self.protocol.artifacts, self.protocol.avilla.global_artifacts]

    @property
    def staff(self):
        return Staff(self.get_staff_artifacts(), self.get_staff_components())


    def message_receive(self) -> AsyncIterator[tuple[Self, dict]]:
        ...

    @property
    def alive(self) -> bool:
        ...

    async def wait_for_available(self):
        ...

    async def send(self, payload: dict) -> None:
        ...

    async def message_handle(self):
        async for connection, data in self.message_receive():
            self.sequence = int(data["id"])

            async def event_parse_task(_data: dict):
                _type = _data["type"]
                with suppress(NotImplementedError):
                    await SatoriCapability(connection.staff).handle_event(_data)
                    return

                logger.warning(f"received unsupported event {_type}: {_data}")

            asyncio.create_task(event_parse_task(data))

    async def connection_closed(self):
        self.close_signal.set()

    async def call(self, action: str, params: dict | None = None) -> None:
        raise NotImplementedError


    async def call_http(
        self,
        action: str,
        account: Selector,
        params: dict | None = None
    ) -> dict:
        ...
