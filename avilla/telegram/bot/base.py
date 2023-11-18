from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, AsyncIterator, Generic, TypeVar

from loguru import logger
from telegram import Update
from typing_extensions import Self

from avilla.core import Selector
from avilla.core.ryanvk.staff import Staff
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.fragments import MessageFragment
from avilla.telegram.utilities import telegram_event_type

if TYPE_CHECKING:
    from avilla.core.ryanvk.protocol import SupportsStaff  # noqa
    from avilla.telegram.account import TelegramAccount  # noqa
    from avilla.telegram.protocol import TelegramProtocol  # noqa


class TelegramBase:
    account: TelegramAccount | None
    protocol: TelegramProtocol
    timeout_signal: asyncio.Event
    kill_switch: asyncio.Event

    def __init__(self, protocol: TelegramProtocol):
        super().__init__()
        self.account = None
        self.protocol = protocol
        self.timeout_signal = asyncio.Event()
        self.kill_switch = asyncio.Event()

    def get_staff_components(self):
        return {"connection": self, "protocol": self.protocol, "avilla": self.protocol.avilla}

    def get_staff_artifacts(self):
        return [self.protocol.artifacts, self.protocol.avilla.global_artifacts]

    @property
    def staff(self):
        return Staff(self.get_staff_artifacts(), self.get_staff_components())

    def message_receive(self) -> AsyncIterator[tuple[Self, Update]]:
        ...

    @property
    def alive(self) -> bool:  # noqa
        ...

    async def wait_for_available(self):
        ...

    async def send(self, target: Selector, fragments: list[MessageFragment]) -> list[int]:
        ...

    async def message_handle(self):
        async for instance, data in self.message_receive():

            async def event_parse_task(_data: Update):
                event_type = telegram_event_type(_data)
                event = await TelegramCapability(instance.staff).handle_event(event_type, _data)
                if event == "non-implemented":
                    logger.warning(f"received unsupported event: {_data}")
                    return
                elif event is not None:
                    await self.protocol.post_event(event)

            asyncio.create_task(event_parse_task(data))
