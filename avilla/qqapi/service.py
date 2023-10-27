from __future__ import annotations

import asyncio  # noqa: F401
from typing import TYPE_CHECKING, Set

from launart import Launart, Service, any_completed

from avilla.qqapi.connection.base import QQAPINetworking
from avilla.qqapi.connection.ws_client import QQAPIWsClientNetworking

if TYPE_CHECKING:
    from .account import QQAPIAccount
    from .protocol import QQAPIProtocol


class QQAPIService(Service):
    id = "qqapi.service"

    protocol: QQAPIProtocol
    connections: list[QQAPIWsClientNetworking]
    accounts: dict[str, QQAPIAccount]

    def __init__(self, protocol: QQAPIProtocol):
        self.protocol = protocol
        self.connections = []
        self.accounts = {}
        super().__init__()

    def has_connection(self, account_id: str):
        return account_id in self.accounts

    def get_connection(self, account_id: str) -> QQAPINetworking:
        return self.accounts[account_id].connection

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
