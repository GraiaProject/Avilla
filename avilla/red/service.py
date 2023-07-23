from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Set

from launart import Launart, Launchable

from .net.base import RedNetworking
from .net.ws_client import RedWsClientNetworking

if TYPE_CHECKING:
    from .protocol import RedProtocol


class RedService(Launchable):
    id = "red.service"

    protocol: RedProtocol
    connections: list[RedWsClientNetworking]

    def __init__(self, protocol: RedProtocol):
        self.protocol = protocol
        self.connections = []
        super().__init__()

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
