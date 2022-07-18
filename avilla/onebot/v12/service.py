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
from graia.amnesia.builtins.aiohttp import AiohttpClientInterface
from graia.broadcast import Broadcast
from launart import Launart, Service
from loguru import logger

from avilla.onebot.v12.connection import OneBot12Connection
from avilla.onebot.v12.connection.config import OneBot12Config

from .account import OneBot12Account

if TYPE_CHECKING:
    from .protocol import OneBot12Protocol


class OneBot12Service(Service):
    id = "OneBot12.service"
    supported_interface_types = {ConnectionInterface}

    protocol: OneBot12Protocol
    connections: dict[OneBot12Account, OneBot12Connection]

    def __init__(self, protocol: OneBot12Protocol):
        self.protocol = protocol
        self.connections = {}
        super().__init__()

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            # TODO: lifecycle event for account
            # 主要有几点 - 配置的读取, 应用; 子任务(Launchable) 的堵塞 - 这个交给 blocking;
            ...

        async with self.stage("blocking"):
            if self.connections:
                await asyncio.gather(
                    conn.status.wait_for("blocking-completed", "waiting-for-cleanup", "cleanup", "finished")
                    for conn in self.connections.values()   
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
