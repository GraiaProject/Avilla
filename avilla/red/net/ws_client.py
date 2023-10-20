from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Literal, cast

import aiohttp
from launart import Service
from launart.manager import Launart
from launart.utilles import any_completed
from loguru import logger

from avilla.red.account import RedAccount
from avilla.red.net.base import RedNetworking
from avilla.standard.core.account import AccountUnregistered, AccountUnavailable

if TYPE_CHECKING:
    from avilla.red.protocol import RedConfig, RedProtocol


class RedWsClientNetworking(RedNetworking, Service):
    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking", "cleanup"}

    config: RedConfig
    connection: aiohttp.ClientWebSocketResponse | None = None
    session: aiohttp.ClientSession

    def __init__(self, protocol: RedProtocol, config: RedConfig) -> None:
        super().__init__(protocol)
        self.config = config

    @property
    def id(self):
        return f"satori/connection/websocket/client#{id(self)}"

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

    async def call_http(
        self, method: Literal["get", "post", "multipart"], action: str, params: dict | None = None, raw: bool = False
    ):
        action = action.replace("_", "/")
        if method == "get":
            async with self.session.get(
                (self.config.http_endpoint / action).with_query(params or {}),
                headers={"Authorization": f"Bearer {self.config.access_token}"},
            ) as resp:
                return (await resp.content.read()) if raw else await resp.json(content_type=None)
        if method == "post":
            async with self.session.post(
                (self.config.http_endpoint / action),
                json=params or {},
                headers={"Authorization": f"Bearer {self.config.access_token}"},
            ) as resp:
                return (await resp.content.read()) if raw else await resp.json(content_type=None)
        if method == "multipart":
            data = aiohttp.FormData(quote_fields=False)
            if params is None:
                raise TypeError("multipart requires params")
            for k, v in params.items():
                if isinstance(v, dict):
                    data.add_field(k, v["value"], filename=v.get("filename"), content_type=v.get("content_type"))
                else:
                    data.add_field(k, v)

            async with self.session.post(
                (self.config.http_endpoint / action),
                data=data,
                headers={"Authorization": f"Bearer {self.config.access_token}"},
            ) as resp:
                return (await resp.content.read()) if raw else await resp.json(content_type=None)
        raise ValueError(f"Unknown method {method}")

    async def wait_for_available(self):
        await self.status.wait_for_available()

    def get_staff_components(self):
        return {"connection": self, "protocol": self.protocol, "avilla": self.protocol.avilla}

    def __staff_generic__(self, element_type: dict, event_type: dict):
        ...

    def get_staff_artifacts(self):
        return [self.protocol.artifacts, self.protocol.avilla.global_artifacts]

    @property
    def alive(self):
        return self.connection is not None and not self.connection.closed

    async def connection_daemon(self, manager: Launart, session: aiohttp.ClientSession):
        while not manager.status.exiting:
            try:
                async with session.ws_connect(
                    self.config.endpoint,
                    timeout=30
                ) as self.connection:
                    logger.info(f"{self} Websocket client connected")
                    self.close_signal.clear()

                    close_task = asyncio.create_task(self.close_signal.wait())
                    receiver_task = asyncio.create_task(self.message_handle())
                    sigexit_task = asyncio.create_task(manager.status.wait_for_sigexit())
                    await self.send(
                        {
                            "type": "meta::connect",
                            "payload": {
                                "token": self.config.access_token,
                            },
                        }
                    )
                    done, pending = await any_completed(
                        sigexit_task,
                        close_task,
                        receiver_task,
                    )
                    avilla = self.protocol.avilla
                    if sigexit_task in done:
                        logger.info(f"{self} Websocket client exiting...")
                        await self.connection.close()
                        self.close_signal.set()
                        self.connection = None
                        for v in list(avilla.accounts.values()):
                            if v.protocol is self.protocol and self.account and v.route["account"] == self.account.route["account"]:  # type: ignore
                                self.account = None
                                del avilla.accounts[v.route]
                                await avilla.broadcast.postEvent(AccountUnregistered(avilla, v.account))
                                return
                    if close_task in done:
                        receiver_task.cancel()
                        logger.warning(f"{self} Connection closed by server, will reconnect in 5 seconds...")
                        for n in list(avilla.accounts.keys()):
                            logger.debug(f"Unregistering red-protocol account {n}...")
                            account = cast("RedAccount", avilla.accounts[n].account)
                            account.status.enabled = False
                            await avilla.broadcast.postEvent(AccountUnavailable(avilla, avilla.accounts[n].account))
                        self.account = None
                        await asyncio.sleep(5)
                        logger.info(f"{self} Reconnecting...")
                        continue
            except Exception as e:
                logger.error(f"{self} Error while connecting: {e}")
                await asyncio.sleep(5)
                logger.info(f"{self} Reconnecting...")

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            self.session = aiohttp.ClientSession()

        async with self.stage("blocking"):
            await self.connection_daemon(manager, self.session)

        async with self.stage("cleanup"):
            await self.session.close()
            self.connection = None
