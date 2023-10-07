from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import TYPE_CHECKING, AsyncIterator, Literal, overload
from typing_extensions import Self

from loguru import logger

from avilla.core.ryanvk.staff import Staff
from avilla.satori.account import SatoriAccount

if TYPE_CHECKING:
    from avilla.satori.protocol import SatoriProtocol


class SatoriNetworking:
    protocol: SatoriProtocol
    accounts: dict[int, SatoriAccount]
    close_signal: asyncio.Event
    sequence: int

    def __init__(self, protocol: SatoriProtocol):
        super().__init__()
        self.protocol = protocol
        self.accounts = {}
        self.close_signal = asyncio.Event()
        self.sequence = 0

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
            event_type = data["type"]
            if not data["payload"]:
                logger.warning(f"received empty event {event_type}")
                continue

            async def event_parse_task(_data: dict):
                _type = _data["type"]
                with suppress(NotImplementedError):
                    await ElizabethCapability(connection.staff).handle_event(_data)
                    return

                logger.warning(f"received unsupported event {_type}: {_data}")

            asyncio.create_task(event_parse_task(data))

    async def connection_closed(self):
        self.close_signal.set()

    async def call(self, action: str, params: dict | None = None) -> None:
        raise NotImplementedError

    @overload
    async def call_http(
        self, method: Literal["get", "post", "multipart"], action: str, params: dict | None = None
    ) -> dict:
        ...

    @overload
    async def call_http(
        self,
        method: Literal["get", "post", "multipart"],
        action: str,
        params: dict | None = None,
        raw: Literal[True] = True,
    ) -> bytes:
        ...

    async def call_http(
        self, method: Literal["get", "post", "multipart"], action: str, params: dict | None = None, raw: bool = False
    ) -> dict | bytes:
        ...
