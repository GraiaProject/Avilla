from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING
from avilla.console.frontend import Frontend
from avilla.standard.core.account import AccountAvailable, AccountUnavailable
from launart import Launart, Launchable

if TYPE_CHECKING:
    from .protocol import ConsoleProtocol


class ConsoleService(Launchable):
    id = "console.service"
    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking", "cleanup"}
    app: Frontend
    protocol: ConsoleProtocol

    def __init__(self, protocol: ConsoleProtocol):
        self.app = Frontend(protocol)
        self.protocol = protocol
        super().__init__()

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            self.protocol.avilla.broadcast.postEvent(AccountAvailable(self.protocol.avilla, self.app.account))
        async with self.stage("blocking"):
            task = asyncio.create_task(self.app.run_async())
            await manager.status.wait_for_sigexit()
        async with self.stage("cleanup"):
            self.app.exit()
            self.protocol.avilla.broadcast.postEvent(AccountUnavailable(self.protocol.avilla, self.app.account))
            if task:
                await task
