from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, AsyncIterator, Generic, Literal, TypeVar

from loguru import logger

from avilla.core.exceptions import InvalidAuthentication
from avilla.core.ryanvk.staff import Staff

from .util import validate_response

if TYPE_CHECKING:
    from avilla.core.ryanvk.protocol import SupportsStaff
    from avilla.elizabeth.protocol import ElizabethProtocol


T = TypeVar("T", bound="SupportsStaff")
CallMethod = Literal["get", "post", "fetch", "update", "multipart"]


class ElizabethNetworking(Generic[T]):
    protocol: ElizabethProtocol
    response_waiters: dict[str, asyncio.Future]
    close_signal: asyncio.Event

    account_id: int
    session_key: str | None = None

    def __init__(self, protocol: ElizabethProtocol):
        super().__init__()
        self.protocol = protocol
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
            if "code" in data:
                validate_response(data)

            sync_id: str = data.get("syncId", "#")
            body: dict | Exception = validate_response(data.get("data"), False)
            if isinstance(body, Exception):
                if sync_id in self.response_waiters:
                    self.response_waiters[sync_id].set_exception(body)
                continue

            if "session" in body:
                self.session_key = body["session"]
                logger.success("session key got.")
                continue

            if sync_id in self.response_waiters:
                self.response_waiters[sync_id].set_result(body)
                continue

            if "type" not in body:
                continue

            async def event_parse_task(data: dict):
                event_type = data["type"]
                event = await Staff.focus(connection).parse_event(event_type, data)
                if event == "non-implemented":
                    logger.warning(f"received unsupported event {event_type}: {data}")
                    return
                elif event is not None:
                    await self.protocol.post_event(event)

            asyncio.create_task(event_parse_task(body))

    async def connection_closed(self):
        self.session_key = None
        self.close_signal.set()

    async def call(
        self,
        method: CallMethod,
        action: str,
        params: dict | None = None,
        *,
        session: bool = True,
    ) -> dict:
        if not self.alive:
            raise RuntimeError("connection is not established")
        if session and self.session_key is None:
            raise InvalidAuthentication

        if method == "multipart":
            return await self.call_http(method, action, params)

        future: asyncio.Future[dict] = asyncio.get_running_loop().create_future()
        echo = str(hash(future))
        self.response_waiters[echo] = future

        try:
            await self.wait_for_available()
            await self.send(
                {
                    "subCommand": {
                        "fetch": "get",
                    }.get(method)
                    or method,
                    "syncId": echo,
                    "command": action,
                    "content": params or {},
                    **({"sessionKey": self.session_key} if session else {}),
                }
            )
            return await future
        finally:
            del self.response_waiters[echo]

    async def call_http(self, method: CallMethod, action: str, params: dict | None = None) -> dict:
        ...
