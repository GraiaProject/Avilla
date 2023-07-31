from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, AsyncIterator, Generic, Literal, TypeVar, overload

from loguru import logger

from avilla.core.ryanvk.staff import Staff
from avilla.red.account import RedAccount

if TYPE_CHECKING:
    from avilla.core.ryanvk.protocol import SupportsStaff  # noqa: F401
    from avilla.red.protocol import RedProtocol


T = TypeVar("T", bound="SupportsStaff")


class RedNetworking(Generic[T]):
    protocol: RedProtocol
    account: RedAccount | None
    close_signal: asyncio.Event

    def __init__(self, protocol: RedProtocol):
        super().__init__()
        self.protocol = protocol
        self.account = None
        self.close_signal = asyncio.Event()

    def message_receive(self) -> AsyncIterator[tuple[T, dict]]:
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

            async def event_parse_task(data: dict):
                event_type = data["type"]
                event = await Staff.focus(connection).parse_event(event_type, data["payload"])
                if event == "non-implemented":
                    logger.warning(f"received unsupported event {event_type}: {data}")
                    return
                elif event is not None:
                    self.protocol.post_event(event)

            asyncio.create_task(event_parse_task(data))

    async def connection_closed(self):
        self.close_signal.set()

    async def call(self, action: str, params: dict | None = None) -> None:
        if not self.alive:
            raise RuntimeError("connection is not established")

        await self.wait_for_available()
        await self.send({"type": action, "payload": params or {}})
        return

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
