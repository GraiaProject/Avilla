from __future__ import annotations

from typing import TYPE_CHECKING

from launart import Launart, Service, any_completed

from avilla.onebot.v11.net.ws_client import OneBot11WsClientNetworking
from avilla.onebot.v11.net.ws_server import OneBot11WsServerNetworking

if TYPE_CHECKING:
    from .protocol import OneBot11Protocol


class OneBot11Service(Service):
    id = "onebot11.service"
    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking", "cleanup"}

    connections: list[OneBot11WsClientNetworking | OneBot11WsServerNetworking]
    protocol: OneBot11Protocol

    def __init__(self, protocol: OneBot11Protocol):
        self.connections = []
        self.protocol = protocol
        super().__init__()

    async def launch(self, manager: Launart):
        for conn in self.connections:
            manager.add_component(conn)

        async with self.stage("preparing"):
            ...

        async with self.stage("blocking"):
            await any_completed(
                manager.status.wait_for_sigexit(),
                *(conn.status.wait_for("blocking-completed") for conn in self.connections),
            )

        async with self.stage("cleanup"):
            pass
