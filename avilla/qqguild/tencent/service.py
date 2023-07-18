from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Set

from avilla.qqguild.tencent.connection.base import QQGuildNetworking
from avilla.qqguild.tencent.connection.ws_client import QQGuildWsClientNetworking
from launart import Launart, Launchable

if TYPE_CHECKING:
    from .protocol import QQGuildProtocol


class QQGuildService(Launchable):
    id = "qqguild.service"

    protocol: QQGuildProtocol
    connections: list[QQGuildWsClientNetworking]
    account_map: dict[str, QQGuildNetworking]

    def __init__(self, protocol: QQGuildProtocol):
        self.protocol = protocol
        self.connections = []
        self.account_map = {}
        super().__init__()

    def has_connection(self, account_id: str):
        return account_id in self.account_map

    def get_connection(self, account_id: str) -> QQGuildNetworking:
        return self.account_map[account_id]

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            # TODO: lifecycle event for account
            # 主要有几点 - 配置的读取，应用; 子任务 (Launchable) 的堵塞 - 这个交给 blocking;
            for i in self.connections:
                manager.add_component(i)

        async with self.stage("blocking"):
            await asyncio.gather(
                manager.status.wait_for_sigexit(), *(i.status.wait_for("blocking-completed") for i in self.connections)
            )

        async with self.stage("cleanup"):
            ...  # TODO

    @property
    def stages(self):
        return {"preparing", "blocking", "cleanup"}

    @property
    def required(self) -> Set[str]:
        return set()
