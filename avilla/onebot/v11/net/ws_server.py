from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import aiohttp.web
from yarl import URL

from avilla.core._vendor.dataclasses import dataclass
from launart import Launchable
from launart.manager import Launart
from launart.utilles import any_completed

if TYPE_CHECKING:
    from v11.protocol import OneBot11Protocol


@dataclass
class OneBot11WsServerConfig:
    endpoint: URL
    access_token: str | None = None


class OneBot11WsServerNetworking(Launchable):
    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking", "cleanup"}

    protocol: OneBot11Protocol
    config: OneBot11WsServerConfig

    signal_close: asyncio.Event
    response_waiters: dict[str, asyncio.Future]

    def __init__(self) -> None:
        super().__init__()
        self.close_signal = asyncio.Event()
        self.response_waiters = {}

    async def websocket_server_handler(self, request: aiohttp.web.Request):
        ws = aiohttp.web.WebSocketResponse()
        await ws.prepare(request)
        # TODO
        return ws

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            # use richuru to redirect log to loguru
            server = aiohttp.web.Application()
            server.add_routes([aiohttp.web.get("/onebot/v11", self.websocket_server_handler)])

        async with self.stage("blocking"):
            task = asyncio.get_running_loop().create_task(aiohttp.web._run_app(server))
            await any_completed(manager.status.wait_for_sigexit(), asyncio.shield(task))

        async with self.stage("cleanup"):
            task.cancel()
