from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from nonechat.app import Frontend
from nonechat.setting import ConsoleSetting

from avilla.standard.core.account import AccountUnavailable
from launart import Launart, Launchable

from .backend import AvillaConsoleBackend

if TYPE_CHECKING:
    from .protocol import ConsoleProtocol


class ConsoleService(Launchable):
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
            )
        )
        self.app.backend.set_service(self)
        self.protocol = protocol
        super().__init__()

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            ...

        async with self.stage("blocking"):
            task = asyncio.create_task(self.app.run_async())
            await manager.status.wait_for_sigexit()
        async with self.stage("cleanup"):
            self.app.exit()
            if task:
                await task
            self.protocol.avilla.broadcast.postEvent(AccountUnavailable(self.protocol.avilla, self.app.backend.account))
