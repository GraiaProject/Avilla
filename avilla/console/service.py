from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from launart import Launart, Service
from nonechat.app import Frontend
from nonechat.setting import ConsoleSetting
from textual.color import Color

from avilla.standard.core.account import AccountUnavailable

from .backend import AvillaConsoleBackend

if TYPE_CHECKING:
    from .protocol import ConsoleProtocol


class ConsoleService(Service):
    id = "console.service"
    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking", "cleanup"}
    app: Frontend[AvillaConsoleBackend]
    protocol: ConsoleProtocol

    def __init__(self, protocol: ConsoleProtocol):
        self.app = Frontend(
            AvillaConsoleBackend,
            ConsoleSetting(
                title="Console",
                sub_title="Welcome to Avilla",
                icon="Avilla",
                icon_color=Color.parse("#22b14c"),
                title_color=Color(229, 192, 123, 1),
                bg_color=Color(40, 44, 52, 1),
                header_color=Color(90, 99, 108, 0.6),
                user_avatar="😃",
            ),
        )
        self.app.backend.set_service(self)
        self.protocol = protocol
        super().__init__()

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            ...

        async with self.stage("blocking"):
            task = asyncio.get_running_loop().create_task(self.app.run_async())
            await manager.status.wait_for_sigexit()
        async with self.stage("cleanup"):
            self.app.exit()
            if task:
                await task
            self.protocol.avilla.broadcast.postEvent(AccountUnavailable(self.protocol.avilla, self.app.backend.account))
