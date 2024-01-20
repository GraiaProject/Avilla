from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

import aiohttp
from launart import Service
from launart.manager import Launart

from avilla.mattermost.connection.base import CallMethod

from .base import MattermostNetworking

if TYPE_CHECKING:
    from avilla.mattermost.protocol import MattermostConfig, MattermostProtocol


class MattermostWsClientNetworking(MattermostNetworking, Service):
    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking", "cleanup"}

    config: MattermostConfig
    connection: aiohttp.ClientWebSocketResponse | None = None
    session: aiohttp.ClientSession

    def __init__(self, protocol: MattermostProtocol, config: MattermostConfig) -> None:
        super().__init__(protocol)
        self.config = config
        self.account_id = f"{self.config.login_id}@{self.config.instance}"

    @property
    def id(self):
        return f"mattermost/connection/websocket/client#{self.account_id}"

    async def message_receive(self):
        if self.connection is None:
            raise RuntimeError("connection is not established")

        async for msg in self.connection:
            if msg.type in {aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSED}:
                self.close_signal.set()
                break
            elif msg.type == aiohttp.WSMsgType.TEXT:
                data: dict = json.loads(cast(str, msg.data))
                yield self, data
        else:
            await self.connection_closed()

    async def send(self, payload: dict):
        if self.connection is None:
            raise RuntimeError("connection is not established")

        await self.connection.send_json(payload)

    async def call_http(self, method: CallMethod, action: str, params: dict | None = None) -> dict:
        ...

    async def wait_for_available(self):
        await self.status.wait_for_available()

    @property
    def alive(self):
        return self.connection is not None and not self.connection.closed

    async def connection_daemon(self, manager: Launart, session: aiohttp.ClientSession):
        while not manager.status.exiting:
            ...

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            self.session = aiohttp.ClientSession()

        async with self.stage("blocking"):
            await self.connection_daemon(manager, self.session)

        async with self.stage("cleanup"):
            await self.session.close()
            self.connection = None
