from __future__ import annotations

import asyncio
import json
from collections import ChainMap
from typing import TYPE_CHECKING, cast

import aiohttp
from loguru import logger
from yarl import URL

from avilla.core._vendor.dataclasses import dataclass
from avilla.elizabeth.connection.base import CallMethod
from launart import Launchable
from launart.manager import Launart
from launart.utilles import any_completed

from .base import ElizabethNetworking
from .util import validate_response

if TYPE_CHECKING:
    from ..protocol import ElizabethProtocol


@dataclass
class ElizabethWsClientConfig:
    base_url: URL
    access_token: str
    qq: int


class ElizabethWsClientNetworking(ElizabethNetworking["ElizabethWsClientNetworking"], Launchable):
    id = "elizabeth/connection/websocket/client"

    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking", "cleanup"}

    config: ElizabethWsClientConfig
    connection: aiohttp.ClientWebSocketResponse | None = None
    session: aiohttp.ClientSession

    def __init__(self, protocol: ElizabethProtocol, config: ElizabethWsClientConfig) -> None:
        super().__init__(protocol)
        self.config = config

    async def message_receive(self):
        if self.connection is None:
            raise RuntimeError("connection is not established")

        async for msg in self.connection:
            logger.debug(f"{msg=}")

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

    async def call_http(self, method: CallMethod, action: str, params: dict | None = None) -> dict | None:
        action = action.replace("_", "/")
        if method in {"get", "fetch"}:
            async with self.session.get((self.config.base_url / action).with_query(params or {})) as resp:
                result = await resp.json()
                validate_response(result)
                return result

        if method in {"post", "update"}:
            async with self.session.post((self.config.base_url / action), json=params or {}) as resp:
                result = await resp.json()
                validate_response(result)
                return result

        if method == "multipart":
            data = aiohttp.FormData(quote_fields=False)
            if params is None:
                raise TypeError("multipart requires params")
            for k, v in params:
                if isinstance(v, dict):
                    data.add_field(k, **v)
                else:
                    data.add_field(k, v)

            async with self.session.post((self.config.base_url / action), data=data) as resp:
                result = await resp.json()
                validate_response(result)
                return result

    async def wait_for_available(self):
        await self.status.wait_for_available()

    def get_staff_components(self):
        return {"connection": self, "protocol": self.protocol, "avilla": self.protocol.avilla}

    def get_staff_artifacts(self):
        return ChainMap(self.protocol.isolate.artifacts, self.protocol.avilla.isolate.artifacts)

    @property
    def alive(self):
        return self.connection is not None and not self.connection.closed

    async def connection_daemon(self, manager: Launart, session: aiohttp.ClientSession):
        while not manager.status.exiting:
            async with session.ws_connect(
                self.config.base_url / "all", params={"verifyKey": self.config.access_token, "qq": str(self.config.qq)}
            ) as self.connection:
                logger.info(f"{self} Websocket client connected")
                self.close_signal.clear()
                close_task = asyncio.create_task(self.close_signal.wait())
                receiver_task = asyncio.create_task(self.message_handle())
                sigexit_task = asyncio.create_task(manager.status.wait_for_sigexit())

                done, pending = await any_completed(
                    sigexit_task,
                    close_task,
                    receiver_task,
                )
                if sigexit_task in done:
                    logger.info(f"{self} Websocket client exiting...")
                    await self.connection.close()
                    self.close_signal.set()
                    self.connection = None
                    # TODO: unregister account
                    return
                if close_task in done:
                    receiver_task.cancel()
                    logger.warning(f"{self} Connection closed by server, will reconnect in 5 seconds...")
                    # TODO: unregister account, including app & conn ref.
                    await asyncio.sleep(5)
                    logger.info(f"{self} Reconnecting...")
                    continue

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            self.session = aiohttp.ClientSession()

        async with self.stage("blocking"):
            await self.connection_daemon(manager, self.session)

        async with self.stage("cleanup"):
            await self.session.close()
            self.connection = None