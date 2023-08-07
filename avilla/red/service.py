from __future__ import annotations

from typing import TYPE_CHECKING, Set

from launart import Launart, Service, any_completed

from .net.ws_client import RedWsClientNetworking

if TYPE_CHECKING:
    from .protocol import RedProtocol


class RedService(Service):
    id = "red.service"

    protocol: RedProtocol
    connections: list[RedWsClientNetworking]

    def __init__(self, protocol: RedProtocol):
        self.protocol = protocol
        self.connections = []
        super().__init__()

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            for i in self.connections:
                manager.add_component(i)

        async with self.stage("blocking"):
            await any_completed(
                manager.status.wait_for_sigexit(), *(i.status.wait_for("blocking-completed") for i in self.connections)
            )

        async with self.stage("cleanup"):
            ...

    @property
    def stages(self):
        return {"preparing", "blocking", "cleanup"}

    @property
    def required(self) -> Set[str]:
        return set()
