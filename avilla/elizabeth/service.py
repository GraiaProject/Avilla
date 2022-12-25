from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from graia.amnesia.transport.common.client import AbstractClientInterface
from launart import Launart, Service

from .connection import ElizabethConnection
from .connection.config import U_Config

if TYPE_CHECKING:
    from .protocol import ElizabethProtocol


class ElizabethService(Service):
    id = "elizabeth.service"
    supported_interface_types = set()

    protocol: ElizabethProtocol
    connections: list[ElizabethConnection[U_Config]]

    def __init__(self, protocol: ElizabethProtocol):
        self.protocol = protocol
        self.connections = []
        super().__init__()

    def has_connection(self, account_id: str):
        return any(conn.config.account == account_id for conn in self.connections)

    def get_connection(self, account_id: str):
        for conn in self.connections:
            if conn.config.account == account_id:
                return conn
        raise ValueError(f"Account {account_id} not found")

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            # TODO: lifecycle event for account
            # 主要有几点 - 配置的读取，应用; 子任务 (Launchable) 的堵塞 - 这个交给 blocking;
            ...

        async with self.stage("blocking"):
            if self.connections:
                await asyncio.wait(
                    [
                        conn.status.wait_for("blocking-completed", "waiting-for-cleanup", "cleanup", "finished")
                        for conn in self.connections
                    ]
                )

        async with self.stage("cleanup"):
            ...  # TODO

    @property
    def required(self):
        return {AbstractClientInterface}

    @property
    def stages(self):
        return {"preparing", "blocking", "cleanup"}

    def get_interface(self, _):
        return None
