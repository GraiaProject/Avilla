from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, AsyncIterator, Generic, Literal, TypeVar

from loguru import logger

from avilla.core.ryanvk.staff import Staff

from ..audit import audit_result, MessageAudited
from .util import Opcode, Payload


if TYPE_CHECKING:
    from avilla.core.ryanvk.protocol import SupportsStaff
    from avilla.qqguild.tencent.protocol import QQGuildProtocol


T = TypeVar("T", bound="SupportsStaff")
CallMethod = Literal["get", "post", "fetch", "update", "multipart", "put", "delete", "patch"]


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
            if data["op"] != Opcode.DISPATCH:
                logger.debug(f"received other payload: {data}")
                continue
            payload = Payload(**data)
            connection.sequence = payload.sequence  # type: ignore

            async def event_parse_task(_data: Payload):
                event_type = _data.type
                if not event_type:
                    raise ValueError("event type is None")
                event = await Staff.focus(connection).parse_event(event_type.lower(), _data.data)
                if event == "non-implemented":
                    logger.warning(f"received unsupported event {event_type.lower()}: {_data.data}")
                    return
                elif event is not None:
                    if isinstance(event, MessageAudited):
                        audit_result.add_result(event)
                    await self.protocol.post_event(event)

            asyncio.create_task(event_parse_task(payload))

    async def connection_closed(self):
        self.session_id = None
        self.close_signal.set()

    async def call(self, method: CallMethod, action: str, params: dict | None = None) -> dict:
        ...
