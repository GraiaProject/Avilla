from __future__ import annotations

import asyncio
import contextlib
import importlib.metadata
from typing import TYPE_CHECKING, Coroutine, Dict, Iterable, List, Optional, Tuple, Type, overload

from aiohttp import ClientSession
from graia.amnesia.builtins.aiohttp import AiohttpClientInterface
from graia.broadcast import Broadcast
from launart import Launart, Service
from loguru import logger

from .connection import (
    CONFIG_MAP,
    ConnectionInterface,
    ConnectionMixin,
    HttpClientConnection,
)
from .connection._info import HttpClientInfo, U_Info
from .exception import AriadneConfigurationError

if TYPE_CHECKING:
    from .protocol import ElizabethProtocol


class ElizabethService(Service):
    id = "elizabeth.service"
    supported_interface_types = {ConnectionInterface}
    http_interface: AiohttpClientInterface
    connections: Dict[int, ConnectionMixin[U_Info]]
    protocol: ElizabethProtocol
    broadcast: Broadcast

    def __init__(self, protocol: ElizabethProtocol) -> None:
        # TODO: protocol pass by
        self.connections = {}
        super().__init__()

    def add_configs(self, configs: Iterable[U_Info]) -> Tuple[List[ConnectionMixin], int]:
        configs = list(configs)
        if not configs:
            raise AriadneConfigurationError("No configs provided")

        account: int = configs[0].account
        if account in self.connections:
            raise AriadneConfigurationError(f"Account {account} already exists")
        if len({i.account for i in configs}) != 1:
            raise AriadneConfigurationError("All configs must be for the same account")

        configs.sort(key=lambda x: isinstance(x, HttpClientInfo))
        # make sure the http client is the last one
        conns: List[ConnectionMixin] = [self.add_info(conf) for conf in configs]
        return conns, account

    def add_info(self, config: U_Info) -> ConnectionMixin:
        account: int = config.account
        connection = CONFIG_MAP[config.__class__](config)
        if account not in self.connections:
            self.connections[account] = connection
        elif isinstance(connection, HttpClientConnection):
            upstream_conn = self.connections[account]
            if upstream_conn.fallback:
                raise ValueError(f"{upstream_conn} already has fallback connection")
            connection.status = upstream_conn.status
            connection.is_hook = True
            upstream_conn.fallback = connection
        else:
            raise ValueError(f"Connection {self.connections[account]} conflicts with {connection}")
        return connection

    async def launch(self, mgr: Launart):
        async with self.stage("preparing"):
            self.http_interface = mgr.get_interface(AiohttpClientInterface)

        async with self.stage("cleanup"):
            logger.info("Elizabeth Service cleaning up...", style="dark_orange")

            for task in asyncio.all_tasks():
                if task.done():
                    continue
                coro: Coroutine = task.get_coro()  # type: ignore
                if coro.__qualname__ == "Broadcast.Executor":
                    task.cancel()
                    logger.debug(f"Cancelling {task.get_name()} (Broadcast.Executor)")
                elif coro.cr_frame.f_globals["__name__"].startswith("graia.scheduler"):
                    task.cancel()
                    logger.debug(f"Cancelling {task.get_name()} (Scheduler Task)")

    @property
    def client_session(self) -> ClientSession:
        return self.http_interface.service.session

    @property
    def required(self):
        return {"http.universal_client"} | {conn.id for conn in self.connections.values()}

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self.broadcast.loop

    @overload
    def get_interface(self, interface_type: Type[ConnectionInterface]) -> ConnectionInterface:
        ...

    @overload
    def get_interface(self, interface_type: type) -> None:
        ...

    def get_interface(self, interface_type: type):
        if interface_type is ConnectionInterface:
            return ConnectionInterface(self)
