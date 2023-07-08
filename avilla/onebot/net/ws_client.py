from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, cast

import aiohttp
from loguru import logger
from yarl import URL

from avilla.core._vendor.dataclasses import dataclass
from avilla.core.exceptions import ActionFailed
from launart import Launchable
from launart.manager import Launart
from launart.utilles import any_completed

from ..account import OneBot11Account
from ..utilles import onebot11_event_type

from devtools import debug

if TYPE_CHECKING:
    from ..protocol import OneBot11Protocol


@dataclass
class OneBot11WsClientConfig:
    endpoint: URL
    access_token: str | None = None


class OneBot11WsClientNetworking(Launchable):
    id = "onebot/v11/connection/websocket/client"

    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking", "cleanup"}

    protocol: OneBot11Protocol
    accounts: dict[int, OneBot11Account]
    config: OneBot11WsClientConfig

    connection: aiohttp.ClientWebSocketResponse | None = None
    signal_close: asyncio.Event
    response_waiters: dict[str, asyncio.Future]

    def __init__(self) -> None:
        super().__init__()
        self.close_signal = asyncio.Event()
        self.response_waiters = {}
        self.accounts = {}

    async def message_receiver(self):
        if self.connection is None:
            raise RuntimeError("connection is not established")

        async for msg in self.connection:
            logger.debug(f"{msg=}")
            if msg.type in {aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSED}:
                self.close_signal.set()
                return
            elif msg.type == aiohttp.WSMsgType.TEXT:
                data: dict = json.loads(cast(str, msg.data))
                #logger.debug(f"{data=}")
                if echo := data.get("echo"):
                    if future := self.response_waiters.get(echo):
                        future.set_result(data)
                    continue
            
                event_type = onebot11_event_type(data)
                event = await self.protocol.parse_event(self, event_type, data)
                if event is not None:
                    debug(event)
                    self.protocol.post_event(event)

    async def call(self, action: str, params: dict | None = None) -> dict | None:
        if self.connection is None:
            raise RuntimeError("connection is not established")

        future: asyncio.Future[dict] = asyncio.get_running_loop().create_future()
        echo = str(hash(future))
        self.response_waiters[echo] = future

        try:
            await self.status.wait_for_available()
            await self.connection.send_json({"action": action, "params": params or {}, "echo": echo})
            result = await future
        finally:
            del self.response_waiters[echo]

        if result["status"] != "ok":
            raise ActionFailed(f"{result['retcode']}: {result}")

        return result["data"]

    async def connection_daemon(self, manager: Launart, session: aiohttp.ClientSession):
        while not manager.status.exiting:
            async with session.ws_connect(
                self.config.endpoint,
                headers={"Authorization": f"Bearer {access_token}"}
                if (access_token := self.config.access_token) is not None
                else None,
            ) as self.connection:
                logger.info(f"{self} Websocket client connected")
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
                    logger.info(f"{self} Websocket client exiting...")
                    await self.connection.close()
                    self.connection = None
                    for k, v in list(self.protocol.avilla.accounts.items()):
                        if v.route["account"] in self.accounts:
                            del self.accounts[k]
                    return
                if close_task in done:
                    receiver_task.cancel()
                    logger.warning(f"{self} Connection closed by server")
                    for i in self.accounts.values():
                        ...  # TODO
                    await asyncio.sleep(5)
                    logger.info(f"{self} Reconnecting...")
                    continue

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            session = aiohttp.ClientSession()

        async with self.stage("blocking"):
            await self.connection_daemon(manager, session)

        async with self.stage("cleanup"):
            await session.close()
            self.connection = None
