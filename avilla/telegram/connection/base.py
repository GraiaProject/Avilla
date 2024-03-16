from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, AsyncIterator

from aiohttp import ClientSession
from loguru import logger
from typing_extensions import Self
from yarl import URL

from avilla.core.ryanvk.staff import Staff
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.connection.util import validate_response

if TYPE_CHECKING:
    from avilla.telegram.account import TelegramAccount  # noqa
    from avilla.telegram.protocol import (  # noqa
        TelegramLongPollingConfig,
        TelegramProtocol,
        TelegramWebhookConfig,
    )


class TelegramNetworking:
    account: TelegramAccount | None
    config: TelegramLongPollingConfig | TelegramWebhookConfig
    protocol: TelegramProtocol
    session: ClientSession

    def __init__(self, protocol: TelegramProtocol):
        super().__init__()
        self.account = None
        self.protocol = protocol

    def get_staff_components(self):
        return {"connection": self, "protocol": self.protocol, "avilla": self.protocol.avilla}

    def get_staff_artifacts(self):
        return [self.protocol.artifacts, self.protocol.avilla.global_artifacts]

    @property
    def staff(self):
        return Staff(self.get_staff_artifacts(), self.get_staff_components())

    def message_receive(self) -> AsyncIterator[tuple[Self, dict[str, ...]]]:
        ...

    @property
    def alive(self) -> bool:  # noqa
        ...

    async def wait_for_available(self):
        ...

    async def send(self, action: str, **kwargs) -> dict:
        ...

    async def message_handle(self):
        async for connection, data in self.message_receive():
            print(f"{data = }")

            async def process_media_group():
                # TODO: re-implement process_media_group
                pass

            async def event_parse_task():
                await TelegramCapability(connection.staff).handle_event(list(data.keys())[-1], data)

            asyncio.create_task(event_parse_task())

    async def call(self, action: str, **data) -> dict:
        # TODO Implement files

        # files: dict[...] = {}
        #
        # if files:
        #     response = await self.send(action, files=files)

        logger.debug(f"calling {action!r}")
        response = await self.send(action, json=data)
        validate_response(response)
        logger.debug(f"call {action!r} success")

        return response
