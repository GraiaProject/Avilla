from __future__ import annotations

import asyncio  # noqa: F401
from typing import TYPE_CHECKING, Set

from launart import Launart, Service, any_completed

from avilla.qqguild.tencent.connection.base import QQGuildNetworking
from avilla.qqguild.tencent.connection.ws_client import QQGuildWsClientNetworking

if TYPE_CHECKING:
    from .account import QQGuildAccount
    from .protocol import QQGuildProtocol


class QQGuildService(Service):
    id = "qqguild/tencent.service"

    protocol: QQGuildProtocol
    connections: list[QQGuildWsClientNetworking]
    accounts: dict[str, QQGuildAccount]

    def __init__(self, protocol: QQGuildProtocol):
        self.protocol = protocol
        self.connections = []
        self.accounts = {}
        super().__init__()

    def has_connection(self, account_id: str):
        return account_id in self.accounts

    def get_connection(self, account_id: str) -> QQGuildNetworking:
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
