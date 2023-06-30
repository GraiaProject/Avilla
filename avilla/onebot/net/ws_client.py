from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, cast

import aiohttp
from loguru import logger
from yarl import URL

from avilla.core._vendor.dataclasses import dataclass
from launart import Launchable
from launart.manager import Launart
from launart.utilles import any_completed

from ..account import OneBot11Account
from ..utilles import onebot11_event_type

if TYPE_CHECKING:
    from ..protocol import OneBot11Protocol


@dataclass
class OneBot11WsClientConfig:
    endpoint: URL
    access_token: str | None = None


class OneBot11WsClientNetworking(Launchable):
    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking", "cleanup"}

    protocol: OneBot11Protocol
    account: OneBot11Account
    config: OneBot11WsClientConfig

    connection: aiohttp.ClientWebSocketResponse | None = None
    signal_close: asyncio.Event
    response_waiters: dict[str, asyncio.Future]

    def __init__(self) -> None:
        super().__init__()
        self.close_signal = asyncio.Event()
        self.response_waiters = {}

    async def message_receiver(self):
        if self.connection is None:
            raise RuntimeError("connection is not established")

        async for msg in self.connection:
            if msg.type in {aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSED}:
                self.close_signal.set()
                return
            elif msg.type == aiohttp.WSMsgType.TEXT:
                data: dict = json.loads(cast(str, msg.data))
                if echo := data.get("echo"):
                    if future := self.response_waiters.get(echo):
                        future.set_result(data)
                    return

                event_type = onebot11_event_type(data)
                event = await self.protocol.parse_event(self.account, event_type, data)
                if event is not None:
                    self.protocol.post_event(event)

    async def connection_daemon(self, manager: Launart, session: aiohttp.ClientSession):
        while not manager.status.exiting:
            async with session.ws_connect(
                self.config.endpoint,
                headers={"Authorization": f"Bearer {access_token}"}
                if (access_token := self.config.access_token) is not None
                else None,
            ) as self.connection:
                self.close_signal.clear()
                close_task = asyncio.create_task(self.close_signal.wait())
                receiver_task = asyncio.create_task(self.message_receiver())
                sigexit_task = asyncio.create_task(manager.status.wait_for_sigexit())
                done, pending = await any_completed(
                    sigexit_task,
                    close_task,
                    receiver_task,
                )
                if sigexit_task in done:
                    logger.info(f"[{self.account.route}] Websocket client exiting...")
                    await self.connection.close()
                    break
                if close_task in done:
                    receiver_task.cancel()
                    logger.warning(f"[{self.account.route}] Connection closed by server")
                    await asyncio.sleep(5)
                    logger.info(f"[{self.account.route}] Reconnecting...")
                    continue

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            session = aiohttp.ClientSession()

        async with self.stage("blocking"):
            await self.connection_daemon(manager, session)

        async with self.stage("cleanup"):
            await session.close()
            self.connection = None
