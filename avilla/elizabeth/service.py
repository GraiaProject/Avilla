from __future__ import annotations

from typing import TYPE_CHECKING, Set

from launart import Launart, Launchable

from .connection.base import ElizabethNetworking

if TYPE_CHECKING:
    from .protocol import ElizabethProtocol


class ElizabethService(Launchable):
    id = "elizabeth.service"

    protocol: ElizabethProtocol
    connections: list[ElizabethNetworking]

    def __init__(self, protocol: ElizabethProtocol):
        self.protocol = protocol
        self.connections = []
        super().__init__()

    def has_connection(self, account_id: str):
        ... # TODO

    def get_connection(self, account_id: str):
        ... # TODO

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            # TODO: lifecycle event for account
            # 主要有几点 - 配置的读取，应用; 子任务 (Launchable) 的堵塞 - 这个交给 blocking;
            ...

        async with self.stage("blocking"):
            if self.connections:
                ...

        async with self.stage("cleanup"):
            ...  # TODO

    @property
    def stages(self):
        return {"preparing", "blocking", "cleanup"}

    @property
    def required(self) -> Set[str]:
        return set()