from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, AsyncIterator, Generic, Literal, TypeVar

from loguru import logger

from avilla.core.ryanvk.staff import Staff

from .util import validate_response, Payload

if TYPE_CHECKING:
    from avilla.core.ryanvk.protocol import SupportsStaff

    from ..protocol import QQGuildProtocol


T = TypeVar("T", bound="SupportsStaff")
CallMethod = Literal["get", "post", "fetch", "update", "multipart"]


class QQGuildNetworking(Generic[T]):
    protocol: QQGuildProtocol
    response_waiters: dict[str, asyncio.Future]
    close_signal: asyncio.Event

    account_id: str
    session_id: str | None

    def __init__(self, protocol: QQGuildProtocol):
        super().__init__()
        self.protocol = protocol
        self.response_waiters = {}
        self.close_signal = asyncio.Event()

    def message_receive(self, shard: tuple[int, int]) -> AsyncIterator[tuple[T, dict]]:
        ...

    @property
    def alive(self) -> bool:
        ...

    async def wait_for_available(self):
        ...

    async def send(self, payload: dict) -> None:
        ...

    async def message_handle(self, shard: tuple[int, int]):
        async for connection, data in self.message_receive(shard):
            if data["op"] != 0:
                logger.debug(f"received other payload: {data}")
                continue
            payload = Payload(**data)
            connection.sequence = payload.sequence  # type: ignore
            async def event_parse_task(data: Payload):
                event_type = data.type
                assert event_type is not None, "event type is None"
                event = await Staff.focus(connection).parse_event(event_type.lower(), data.data)
                if event is None:
                    logger.warning(f"received unsupported event {event_type.lower()}: {data.data}")
                    return
                # logger.debug(f"{data['self_id']} received event {event_type}")
                await self.protocol.post_event(event)

            asyncio.create_task(event_parse_task(payload))

    async def connection_closed(self):
        self.session_id = None
        self.close_signal.set()

    async def call(self, method: CallMethod, action: str, params: dict | None = None) -> dict | None:
        ...
