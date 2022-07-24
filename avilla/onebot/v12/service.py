from __future__ import annotations

import asyncio
import contextlib
import importlib.metadata
from typing import (
    TYPE_CHECKING,
    Coroutine,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    overload,
)

from aiohttp import ClientSession
from avilla.onebot.v12.connect import OneBot12Connection
from graia.amnesia.builtins.aiohttp import AiohttpClientInterface
from graia.broadcast import Broadcast
from launart import Launart, Service
from loguru import logger

from avilla.elizabeth.account import ElizabethAccount

if TYPE_CHECKING:
    from .protocol import OneBot12Protocol


class ElizabethService(Service):
    id = "onebot.v12.service"
    supported_interface_types = {ConnectionInterface}

    protocol: OneBot12Protocol
    connections: list[OneBot12Connection]

    def __init__(self, protocol: OneBot12Protocol):
        self.protocol = protocol
        self.connections = []
        super().__init__()

    # DEBUG 用.
    def ensure_config(self, connection: OneBot12Connection):
        self.connections.append(connection)
        # connection 自己会管理 account.

    def get_conn(self, account_id: int):
        for conn in self.connections:
            if conn.config.account == account_id:
                return conn

    def has_account(self, account_id: int):
        return any(conn.config.account == account_id for conn in self.connections)

    def get_account(self, account_id: int):
        for conn in self.connections:
            if conn.config.account == account_id:
                return conn
        raise ValueError(f"Account {account_id} not found")

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            # TODO: lifecycle event for account
            # 主要有几点 - 配置的读取, 应用; 子任务(Launchable) 的堵塞 - 这个交给 blocking;
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
    def required(self) -> set[str]:
        return {"http.universal_client"}

    @property
    def stages(self):
        return {"preparing", "blocking", "cleanup"}

    @overload
    def get_interface(self, interface_type: Type[ConnectionInterface]) -> ConnectionInterface:
        ...

    @overload
    def get_interface(self, interface_type: type) -> None:
        ...

    def get_interface(self, interface_type: type):
        if interface_type is ConnectionInterface:
            return ConnectionInterface(self)
