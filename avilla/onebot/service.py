from __future__ import annotations

from asyncio import gather
from typing import TYPE_CHECKING

from launart import Launart, Launchable

from .connection import OneBot11Connection

if TYPE_CHECKING:
    from .protocol import OneBot11Protocol


class OneBot11Service(Launchable):
    id = "onebot11.service"
    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking", "cleanup"}

    connections: list[OneBot11Connection]
    protocol: OneBot11Protocol

    def __init__(self, protocol: OneBot11Protocol):
        self.connections = []
        self.protocol = protocol
        super().__init__()

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            ...

        async with self.stage("blocking"):
            await gather(
                manager.status.wait_for_sigexit(),
                *(conn.status.wait_for("blocking-completed") for conn in self.connections),
            )

        async with self.stage("cleanup"):
            pass
