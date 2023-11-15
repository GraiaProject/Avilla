from __future__ import annotations

import asyncio
from contextlib import suppress
from datetime import datetime
from typing import TYPE_CHECKING, AsyncIterator, Literal

from loguru import logger
from typing_extensions import Self

from avilla.core.ryanvk.staff import Staff
from avilla.qqapi.audit import MessageAudited, audit_result
from avilla.qqapi.capability import QQAPICapability

from .util import Opcode, Payload

if TYPE_CHECKING:
    from avilla.qqapi.protocol import QQAPIProtocol

CallMethod = Literal["get", "post", "fetch", "update", "multipart", "put", "delete", "patch"]


class QQAPINetworking:
    protocol: QQAPIProtocol
    response_waiters: dict[str, asyncio.Future]
    close_signal: asyncio.Event

    account_id: str
    self_info: dict
    sequence: int | None
    session_id: str | None
    _access_token: str | None
    _expires_in: datetime | None

    def __init__(self, protocol: QQAPIProtocol):
        super().__init__()
        self.protocol = protocol
        self.response_waiters = {}
        self.close_signal = asyncio.Event()
        self.session_id = None
        self.sequence = None
        self._access_token = None
        self._expires_in = None

    def get_staff_components(self):
        return {"connection": self, "protocol": self.protocol, "avilla": self.protocol.avilla}

    def get_staff_artifacts(self):
        return [self.protocol.artifacts, self.protocol.avilla.global_artifacts]

    @property
    def staff(self):
        return Staff(self.get_staff_artifacts(), self.get_staff_components())

    def message_receive(self, shard: tuple[int, int]) -> AsyncIterator[tuple[Self, dict]]:
        ...

    @property
    def alive(self) -> bool:
        ...

    async def wait_for_available(self):
        ...

    async def send(self, payload: dict, shard: tuple[int, int]) -> None:
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
                with suppress(NotImplementedError):
                    event = await QQAPICapability(connection.staff).event_callback(event_type.lower(), _data.data)
                    if event is not None:
                        if isinstance(event, MessageAudited):
                            audit_result.add_result(event)
                        await self.protocol.post_event(event)  # type: ignore
                    return
                logger.warning(f"received unsupported event {event_type.lower()}: {_data.data}")
                return

            asyncio.create_task(event_parse_task(payload))

    async def connection_closed(self):
        self.session_id = None
        self.close_signal.set()

    async def call_http(self, method: CallMethod, action: str, params: dict | None = None) -> dict:
        ...
