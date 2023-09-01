from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, AsyncIterator, Generic, TypeVar

from loguru import logger

from avilla.core.exceptions import ActionFailed
from avilla.core.ryanvk.staff import Staff
from avilla.onebot.v11.utilles import onebot11_event_type

if TYPE_CHECKING:
    from avilla.core.ryanvk.protocol import SupportsStaff
    from avilla.onebot.v11.account import OneBot11Account
    from avilla.onebot.v11.protocol import OneBot11Protocol


T = TypeVar("T", bound="SupportsStaff")


class OneBot11Networking(Generic[T]):
    protocol: OneBot11Protocol
    accounts: dict[int, OneBot11Account]
    response_waiters: dict[str, asyncio.Future]
    close_signal: asyncio.Event

    def __init__(self, protocol: OneBot11Protocol):
        super().__init__()
        self.protocol = protocol
        self.accounts = {}
        self.response_waiters = {}
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
            if echo := data.get("echo"):
                if future := self.response_waiters.get(echo):
                    future.set_result(data)
                continue

            async def event_parse_task(data: dict):
                event_type = onebot11_event_type(data)
                event = await Staff.focus(connection).parse_event(event_type, data)
                if event == "non-implemented":
                    logger.warning(f"received unsupported event {event_type}: {data}")
                    return
                elif event is not None:
                    await self.protocol.post_event(event)

            asyncio.create_task(event_parse_task(data))

    async def connection_closed(self):
        self.close_signal.set()

    async def call(self, action: str, params: dict | None = None) -> dict | None:
        if not self.alive:
            raise RuntimeError("connection is not established")

        future: asyncio.Future[dict] = asyncio.get_running_loop().create_future()
        echo = str(hash(future))
        self.response_waiters[echo] = future

        try:
            await self.wait_for_available()
            await self.send({"action": action, "params": params or {}, "echo": echo})
            result = await future
        finally:
            del self.response_waiters[echo]

        if result["status"] != "ok":
            raise ActionFailed(f"{result['retcode']}: {result}")

        return result.get("data")
