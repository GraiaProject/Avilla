from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, AsyncIterator

from loguru import logger
from typing_extensions import Self

from avilla.core import Selector
from avilla.core.ryanvk.staff import Staff
from avilla.telegram.utilities import reveal_event_type

if TYPE_CHECKING:
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

            async def process_media_group(event_type: str, _data: Update):
                # TODO: re-implement process_media_group
                pass

            async def event_parse_task(_data: Update):
                if (event_type := reveal_event_type(_data)) == "non-implemented":
                    logger.warning(f"received unsupported event: {_data}")
                    return
                # TODO: re-implement event_parse_task

            asyncio.create_task(event_parse_task(data))
