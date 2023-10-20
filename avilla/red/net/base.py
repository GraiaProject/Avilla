from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import TYPE_CHECKING, AsyncIterator, Literal, overload
from typing_extensions import Self

from loguru import logger

from avilla.core.ryanvk.staff import Staff
from avilla.red.account import RedAccount
from avilla.red.capability import RedCapability
from avilla.red.utils import MsgType, get_msg_types

if TYPE_CHECKING:
    from avilla.red.protocol import RedProtocol


class RedNetworking:
    protocol: RedProtocol
    account: RedAccount | None
    close_signal: asyncio.Event

    def __init__(self, protocol: RedProtocol):
        super().__init__()
        self.protocol = protocol
        self.account = None
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
            event_type = data["type"]
            if not data["payload"]:
                logger.warning(f"received empty event {event_type}")
                continue

            async def event_parse_task(t: str, payload: dict):
                with suppress(NotImplementedError):
                    await RedCapability(connection.staff).handle_event(t, payload)
                    return
                logger.warning(f"received unsupported event {t}: {payload}")

            def handle_message(message: dict):
                types = get_msg_types(message)
                if types.msg == MsgType.system and types.send == "system":
                    if (
                        message["subMsgType"] == 8
                        and message["elements"][0]["elementType"] == 8
                        and message["elements"][0]["grayTipElement"]["subElementType"] == 4
                        and message["elements"][0]["grayTipElement"]["groupElement"]["type"] == 1
                    ):
                        asyncio.create_task(event_parse_task("group::member::add", message))
                    elif (
                        message["subMsgType"] == 8
                        and message["elements"][0]["elementType"] == 8
                        and message["elements"][0]["grayTipElement"]["subElementType"] == 4
                        and message["elements"][0]["grayTipElement"]["groupElement"]["type"] == 8
                    ):
                        asyncio.create_task(event_parse_task("group::member::mute", message))
                    elif (
                        message["subMsgType"] == 8
                        and message["elements"][0]["elementType"] == 8
                        and message["elements"][0]["grayTipElement"]["subElementType"] == 4
                        and message["elements"][0]["grayTipElement"]["groupElement"]["type"] == 5
                    ):
                        asyncio.create_task(event_parse_task("group::name_update", message))
                    elif (
                        message["subMsgType"] == 12
                        and message["elements"][0]["elementType"] == 8
                        and message["elements"][0]["grayTipElement"]["subElementType"] == 12
                        and message["elements"][0]["grayTipElement"]["xmlElement"]["busiType"] == "1"
                        and message["elements"][0]["grayTipElement"]["xmlElement"]["busiId"] == "10145"
                    ):
                        asyncio.create_task(event_parse_task("group::member::legacy::add::invited", message))
                    else:
                        logger.warning(f"received unsupported event: {message}")
                        return
                else:
                    asyncio.create_task(event_parse_task("message::recv", message))

            if event_type == "message::recv":
                for msg in data["payload"]:
                    handle_message(msg)
            else:
                asyncio.create_task(event_parse_task(event_type, data["payload"]))

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
