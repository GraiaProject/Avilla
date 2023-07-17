from __future__ import annotations

import asyncio
import json
import sys
from collections import ChainMap
from contextlib import suppress
from typing import TYPE_CHECKING, cast
from dataclasses import asdict

import aiohttp
from loguru import logger
from yarl import URL

from avilla.core._vendor.dataclasses import dataclass, field
from avilla.core.account import AccountInfo
from avilla.core.selector import Selector
from avilla.standard.core.account import AccountAvailable
from launart import Launchable
from launart.manager import Launart
from launart.utilles import any_completed

from ..account import QQGuildAccount
from ..const import PLATFORM
from .base import QQGuildNetworking, CallMethod
from .util import validate_response, Payload

if TYPE_CHECKING:
    from ..protocol import QQGuildProtocol


@dataclass
class Intents:
    guilds: bool = True
    guild_members: bool = True
    guild_messages: bool = False
    guild_message_reactions: bool = True
    direct_message: bool = False
    message_audit: bool = False
    forum_event: bool = False
    audio_action: bool = False
    at_messages: bool = True

    def to_int(self) -> int:
        return (
            self.guilds << 0
            | self.guild_members << 1
            | self.guild_messages << 9
            | self.guild_message_reactions << 10
            | self.direct_message << 12
            | self.message_audit << 27
            | self.forum_event << 28
            | self.audio_action << 29
            | self.at_messages << 30
        )



@dataclass
class QQGuildWsClientConfig:
    id: str
    token: str
    secret: str
    shard: tuple[int, int] = (0, 1)
    intent: Intents = field(default_factory=Intents)
    is_sandbox: bool = False
    api_base: URL = URL("https://api.sgroup.qq.com/")
    sandbox_api_base: URL = URL("https://sandbox.api.sgroup.qq.com")

    def get_api_base(self) -> URL:
        return URL(self.sandbox_api_base) if self.is_sandbox else URL(self.api_base)

    def get_authorization(self) -> str:
        return f"Bot {self.id}.{self.token}"

class QQGuildWsClientNetworking(QQGuildNetworking["QQGuildWsClientNetworking"], Launchable):
    id = "qqguild/connection/client"

    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking", "cleanup"}

    config: QQGuildWsClientConfig
    connection: aiohttp.ClientWebSocketResponse | None = None
    session: aiohttp.ClientSession
    sequence: int | None

    def __init__(self, protocol: QQGuildProtocol, config: QQGuildWsClientConfig) -> None:
        super().__init__(protocol)
        self.config = config
        self.session_id = None
        self.sequence = None

    @property
    def account_id(self):
        return self.config.id

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
                if data["op"] in {7, 9}:
                    break
                yield self, data
        else:
            await self.connection_closed()

    async def send(self, payload: dict):
        if self.connection is None:
            raise RuntimeError("connection is not established")

        await self.connection.send_json(payload)

    async def call(self, method: CallMethod, action: str, params: dict | None = None) -> dict:
        action = action.replace("_", "/")
        params = params or {}
        params = {k: v for k, v in params.items() if v is not None}
        if method in {"get", "fetch"}:
            async with self.session.get(
                (self.config.get_api_base() / action).with_query(params),
                headers={"Authorization": self.config.get_authorization()},
            ) as resp:
                result = await resp.json()
                validate_response(result, resp.status)
                return result

        if method in {"post", "update"}:
            async with self.session.post(
                (self.config.get_api_base() / action),
                json=params,
                headers={"Authorization": self.config.get_authorization()},
            ) as resp:
                result = await resp.json()
                validate_response(result, resp.status)
                return result

        if method == "multipart":
            data = aiohttp.FormData(quote_fields=False)
            if params is None:
                raise TypeError("multipart requires params")
            for k, v in params.items():
                if isinstance(v, dict):
                    data.add_field(k, **v)
                else:
                    data.add_field(k, v)

            async with self.session.post(
                (self.config.get_api_base() / action),
                data=data,
                headers={"Authorization": self.config.get_authorization()},
            ) as resp:
                result = await resp.json()
                validate_response(result, resp.status)
                return result

        raise ValueError(f"unknown method {method}")

    async def wait_for_available(self):
        await self.status.wait_for_available()

    def get_staff_components(self):
        return {"connection": self, "protocol": self.protocol, "avilla": self.protocol.avilla}

    def get_staff_artifacts(self):
        return ChainMap(self.protocol.isolate.artifacts, self.protocol.avilla.isolate.artifacts)

    def __staff_generic__(self, element_type: dict, event_type: dict):
        ...

    @property
    def alive(self):
        return self.connection is not None and not self.connection.closed

    async def _hello(self) -> int | None:
        """接收并处理服务器的 Hello 事件"""
        if self.connection is None:
            raise RuntimeError("connection is not established")
        try:
            payload = Payload(**await self.connection.receive_json())
            return payload.data["heartbeat_interval"]
        except Exception as e:
            logger.error(
                "Error while receiving server hello event",
                e,
            )

    async def _authenticate(self, shard: tuple[int, int] = (0, 1)):
        """鉴权连接"""
        if self.connection is None:
            raise RuntimeError("connection is not established")
        if not self.session_id:
            payload = Payload(
                op=2,
                d={
                    "token": self.config.get_authorization(),
                    "intents": self.config.intent.to_int(),
                    "shard": list(self.config.shard),
                    "properties": {
                        "$os": sys.platform,
                        "$sdk": "Avilla",
                    },
                },
            )
        else:
            payload = Payload(
                op=6,
                d={
                    "token": self.config.get_authorization(),
                    "session_id": self.session_id,
                    "seq": self.sequence,
                },
            )

        try:
            await self.send(asdict(payload))
        except Exception as e:
            logger.error(
                "Error while sending" + (
                    "Identify" if payload.op == 2 else "Resume"
                ) + " event",
                e,
            )
            return

        if not self.session_id:
            # https://bot.q.qq.com/wiki/develop/api/gateway/reference.html#_2-%E9%89%B4%E6%9D%83%E8%BF%9E%E6%8E%A5
            # 鉴权成功之后，后台会下发一个 Ready Event
            payload = Payload(**await self.connection.receive_json())
            assert (payload.op == 0 and payload.t == "READY" and payload.d), f"Received unexpected payload: {payload}"
            self.sequence = payload.s
            self.session_id = payload.d["session_id"]
            account_route = Selector().land("qqguild").account(payload.d["user"]["id"])
            if account_route in self.protocol.avilla.accounts:
                account = cast(QQGuildAccount, self.protocol.avilla.accounts[account_route].account)
            else:
                account = QQGuildAccount(account_route, self.protocol.avilla, self.protocol)
                self.protocol.avilla.accounts[account_route] = AccountInfo(
                    account_route,
                    account,
                    self.protocol,
                    PLATFORM,
                )
            self.protocol.service.account_map[self.config.id] = self
            self.protocol.avilla.broadcast.postEvent(
                AccountAvailable(self.protocol.avilla, account)
            )

        return True

    async def _heartbeat(self, heartbeat_interval: int):
        """心跳"""
        while True:
            if self.sequence:
                try:
                    await self.send({"op": 1, "d": self.sequence})
                except Exception:
                    pass
            await asyncio.sleep(heartbeat_interval / 1000)

    async def connection_daemon(
        self,
        manager: Launart,
        session: aiohttp.ClientSession,
        shard: dict,
    ):
        ws_url = shard["url"]
        remain = shard.get("session_start_limit", {}).get("remaining", 0)
        if remain <= 0:
            raise RuntimeError("No session available")
        while not manager.status.exiting:
            async with session.ws_connect(ws_url, timeout=30) as self.connection:
                logger.info(f"{self} Websocket client connected")
                heartbeat_interval = await self._hello()
                if not heartbeat_interval:
                    await asyncio.sleep(3)
                    continue
                result = await self._authenticate(self.config.shard)
                if not result:
                    await asyncio.sleep(3)
                    continue
                account_route = Selector().land("qqguild").account(self.config.id)
                self.close_signal.clear()
                close_task = asyncio.create_task(self.close_signal.wait())
                receiver_task = asyncio.create_task(self.message_handle())
                sigexit_task = asyncio.create_task(manager.status.wait_for_sigexit())
                heartbeat_task = asyncio.create_task(self._heartbeat(heartbeat_interval))
                done, pending = await any_completed(
                    sigexit_task,
                    close_task,
                    receiver_task,
                    heartbeat_task,
                )
                if sigexit_task in done:
                    logger.info(f"{self} Websocket client exiting...")
                    await self.connection.close()
                    self.close_signal.set()
                    self.connection = None
                    with suppress(KeyError):
                        del self.protocol.service.account_map[self.config.id]
                        del self.protocol.avilla.accounts[account_route]
                    return
                if close_task in done:
                    receiver_task.cancel()
                    heartbeat_task.cancel()
                    logger.warning(f"{self} Connection closed by server, will reconnect in 5 seconds...")

                    with suppress(KeyError):
                        del self.protocol.service.account_map[self.config.id]
                        del self.protocol.avilla.accounts[account_route]
                    await asyncio.sleep(5)
                    logger.info(f"{self} Reconnecting...")
                    continue

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            self.session = aiohttp.ClientSession()
            gateway_info = await self.call("get", "gateway/bot")

        async with self.stage("blocking"):
            await self.connection_daemon(manager, self.session, gateway_info)

        async with self.stage("cleanup"):
            await self.session.close()
            self.connection = None
