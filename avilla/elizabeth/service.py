from __future__ import annotations

from typing import TYPE_CHECKING, Set

from launart import Launart, Service, any_completed

from .connection.base import ElizabethNetworking
from .connection.ws_client import ElizabethWsClientNetworking

if TYPE_CHECKING:
    from .protocol import ElizabethProtocol


class ElizabethService(Service):
    id = "elizabeth.service"

    protocol: ElizabethProtocol
    connections: list[ElizabethWsClientNetworking]
    account_map: dict[int, ElizabethNetworking]

    def __init__(self, protocol: ElizabethProtocol):
        self.protocol = protocol
        self.connections = []
        self.account_map = {}
        super().__init__()

    def has_connection(self, account_id: str):
        return int(account_id) in self.account_map

    def get_connection(self, account_id: str) -> ElizabethNetworking:
        return self.account_map[int(account_id)]

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
