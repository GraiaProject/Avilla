from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import TYPE_CHECKING, AsyncIterator, Literal, TypeVar

from typing_extensions import Self

from avilla.core.exceptions import InvalidAuthentication
from avilla.core.ryanvk.staff import Staff

if TYPE_CHECKING:
    from avilla.mattermost.protocol import MattermostProtocol


T = TypeVar("T", bound="MattermostNetworking")
CallMethod = Literal["get", "post", "fetch", "update", "multipart"]


class MattermostNetworking:
    protocol: MattermostProtocol
    response_waiters: dict[str, asyncio.Future]
    close_signal: asyncio.Event

    account_id: str
    session_key: str | None = None

    def __init__(self, protocol: MattermostProtocol):
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
            ...

            async def event_parse_task(data: dict):
                with suppress(NotImplementedError):
                    # TODO: handle event
                    # await MattermostCapability(connection.staff).handle_event(data)
                    return

            asyncio.create_task(event_parse_task(...))

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
            await self.call_http(..., ...)  # TODO: Obtain token
            await self.send(...)  # TODO: Authenticate using token
            return await future
        finally:
            del self.response_waiters[echo]

    async def call_http(self, method: CallMethod, action: str, params: dict | None = None) -> dict:
        ...
