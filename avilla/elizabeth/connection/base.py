from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import TYPE_CHECKING, AsyncIterator, Literal, TypeVar

from loguru import logger
from typing_extensions import Self

from avilla.core.exceptions import InvalidAuthentication
from avilla.core.ryanvk.staff import Staff
from avilla.core.selector import Selector
from avilla.elizabeth.capability import ElizabethCapability
from avilla.standard.core.account import AccountAvailable

from .util import validate_response

if TYPE_CHECKING:
    from avilla.elizabeth.protocol import ElizabethProtocol


T = TypeVar("T", bound="ElizabethNetworking")
CallMethod = Literal["get", "post", "fetch", "update", "multipart"]


class ElizabethNetworking:
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
                account_route = Selector().land("qq").account(str(self.account_id))
                account = self.protocol.avilla.accounts[account_route].account
                self.protocol.avilla.broadcast.postEvent(AccountAvailable(self.protocol.avilla, account))
                continue

            if sync_id in self.response_waiters:
                self.response_waiters[sync_id].set_result(body)
                continue

            if "type" not in body:
                continue

            async def event_parse_task(data: dict):
                event_type = data["type"]
                with suppress(NotImplementedError):
                    await ElizabethCapability(connection.staff).handle_event(data)
                    return

                logger.warning(f"received unsupported event {event_type}: {data}")

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
                        "update": "post",
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
