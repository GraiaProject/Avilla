from __future__ import annotations

import asyncio
import json
import sys
from collections import ChainMap
from contextlib import suppress
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, cast

import aiohttp
from loguru import logger
from yarl import URL

from avilla.core.account import AccountInfo
from avilla.core.selector import Selector
from avilla.standard.core.account import (
    AccountAvailable,
    AccountRegistered,
    AccountUnavailable,
    AccountUnregistered,
)
from launart import Launchable
from launart.manager import Launart
from launart.utilles import any_completed

from ..account import QQGuildAccount
from ..const import PLATFORM
from .base import CallMethod, QQGuildNetworking
from .util import Payload, validate_response, Opcode

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

    def __post_init__(self):
        if self.at_messages and self.guild_messages:
            logger.warning("at_messages and guild_messages are both enabled, which is not recommended.")

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
    shard: tuple[int, int] | None = None
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
    connections: dict[tuple[int, int], aiohttp.ClientWebSocketResponse]
    session: aiohttp.ClientSession
    sequence: int | None

    def __init__(self, protocol: QQGuildProtocol, config: QQGuildWsClientConfig) -> None:
        super().__init__(protocol)
        self.config = config
        if any([not config.id, not config.token, not config.secret]):
            raise ValueError("config is not complete")
        self.connections = {}
        self.session_id = None
        self.sequence = None

    @property
    def account_id(self):
        return self.config.id

    async def message_receive(self, shard: tuple[int, int]):
        if (connection := self.connections.get(shard)) is None:
            raise RuntimeError("connection is not established")

        async for msg in connection:
            logger.debug(f"{msg=}")

            if msg.type in {aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSED}:
                self.close_signal.set()
                break
            elif msg.type == aiohttp.WSMsgType.TEXT:
                data: dict = json.loads(cast(str, msg.data))
                if data["op"] == 7:
                    break
                if data["op"] == 9:
                    self.session_id = None
                    self.sequence = None
                    break
                yield self, data
        else:
            await self.connection_closed()

    async def connection_closed(self):
        self.session_id = None
        self.sequence = None
        self.close_signal.set()

    async def send(self, payload: dict, shard: tuple[int, int]):
        if (connection := self.connections.get(shard)) is None:
            raise RuntimeError("connection is not established")

        await connection.send_json(payload)

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

        if method == "delete":
            async with self.session.delete(
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
                    data.add_field(k, v["value"], filename=v.get("filename"), content_type=v.get("content_type"))
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
        return self.connections and any(not connection.closed for connection in self.connections.values())

    async def _hello(self, shard: tuple[int, int]) -> int | None:
        """接收并处理服务器的 Hello 事件"""
        if not (connection := self.connections.get(shard)):
            raise RuntimeError("connection is not established")
        try:
            payload = Payload(**await connection.receive_json())
            return payload.data["heartbeat_interval"]
        except Exception as e:
            logger.error(
                "Error while receiving server hello event",
                e,
            )

    async def _authenticate(self, shard: tuple[int, int]):
        """鉴权连接"""
        if not (connection := self.connections.get(shard)):
            raise RuntimeError("connection is not established")
        if not self.session_id:
            payload = Payload(
                op=Opcode.IDENTIFY,
                d={
                    "token": self.config.get_authorization(),
                    "intents": self.config.intent.to_int(),
                    "shard": list(shard),
                    "properties": {
                        "$os": sys.platform,
                        "$sdk": "Avilla",
                    },
                },
            )
        else:
            payload = Payload(
                op=Opcode.RESUME,
                d={
                    "token": self.config.get_authorization(),
                    "session_id": self.session_id,
                    "seq": self.sequence,
                },
            )

        try:
            await self.send(asdict(payload), shard)
        except Exception as e:
            logger.error(f"Error while sending {payload.opcode.name.title()} event: {e}")
            return

        if not self.session_id:
            # https://bot.q.qq.com/wiki/develop/api/gateway/reference.html#_2-%E9%89%B4%E6%9D%83%E8%BF%9E%E6%8E%A5
            # 鉴权成功之后，后台会下发一个 Ready Event
            payload = Payload(**await connection.receive_json())
            assert payload.opcode == Opcode.DISPATCH and payload.type == "READY" and payload.data, f"Received unexpected payload: {payload}"
            self.sequence = payload.sequence
            self.session_id = payload.data["session_id"]
            account_route = Selector().land("qqguild").account(self.config.id)
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
            self.protocol.avilla.broadcast.postEvent(AccountRegistered(self.protocol.avilla, account))

        return True

    async def _heartbeat(self, heartbeat_interval: int, shard: tuple[int, int]):
        """心跳"""
        while True:
            if self.sequence:
                with suppress(Exception):
                    await self.send({"op": 1, "d": self.sequence}, shard=shard)
            await asyncio.sleep(heartbeat_interval / 1000)

    async def connection_daemon(
        self, manager: Launart, session: aiohttp.ClientSession, url: str, shard: tuple[int, int]
    ):
        while not manager.status.exiting:
            async with session.ws_connect(url, timeout=30) as conn:
                self.connections[shard] = conn
                logger.info(f"{self} Websocket client connected")
                heartbeat_interval = await self._hello(shard)
                if not heartbeat_interval:
                    await asyncio.sleep(3)
                    continue
                result = await self._authenticate(shard)
                if not result:
                    await asyncio.sleep(3)
                    continue
                account_route = Selector().land("qqguild").account(self.config.id)
                self.protocol.avilla.broadcast.postEvent(
                    AccountAvailable(self.protocol.avilla, self.protocol.avilla.accounts[account_route].account)
                )
                self.close_signal.clear()
                close_task = asyncio.create_task(self.close_signal.wait())
                receiver_task = asyncio.create_task(self.message_handle(shard))
                sigexit_task = asyncio.create_task(manager.status.wait_for_sigexit())
                heartbeat_task = asyncio.create_task(self._heartbeat(heartbeat_interval, shard))
                done, pending = await any_completed(
                    sigexit_task,
                    close_task,
                    receiver_task,
                    heartbeat_task,
                )
                if sigexit_task in done:
                    logger.info(f"{self} Websocket client exiting...")
                    await conn.close()
                    self.close_signal.set()
                    with suppress(KeyError):
                        del self.connections[shard]
                        await self.protocol.avilla.broadcast.postEvent(
                            AccountUnavailable(
                                self.protocol.avilla, self.protocol.avilla.accounts[account_route].account
                            )
                        )
                        del self.protocol.service.account_map[self.config.id]
                        del self.protocol.avilla.accounts[account_route]
                    return
                if close_task in done:
                    receiver_task.cancel()
                    heartbeat_task.cancel()
                    logger.warning(f"{self} Connection closed by server, will reconnect in 5 seconds...")

                    with suppress(KeyError):
                        await self.protocol.avilla.broadcast.postEvent(
                            AccountUnregistered(
                                self.protocol.avilla, self.protocol.avilla.accounts[account_route].account
                            )
                        )
                        del self.protocol.service.account_map[self.config.id]
                        del self.protocol.avilla.accounts[account_route]
                    await asyncio.sleep(5)
                    logger.info(f"{self} Reconnecting...")
                    continue

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            self.session = aiohttp.ClientSession()
            gateway_info = await self.call("get", "gateway/bot")
            ws_url = gateway_info["url"]
            remain = gateway_info.get("session_start_limit", {}).get("remaining")
            if remain is not None and remain <= 0:
                logger.error("Session start limit reached, please wait for a while")
                manager.status.exiting = True
                return
        tasks = []
        async with self.stage("blocking"):
            if self.config.shard:
                tasks.append(
                    asyncio.create_task(self.connection_daemon(manager, self.session, ws_url, self.config.shard))
                )
            else:
                shards = gateway_info.get("shards") or 1
                print(shards)
                for i in range(shards):
                    tasks.append(
                        asyncio.create_task(self.connection_daemon(manager, self.session, ws_url, (i, shards)))
                    )
                    await asyncio.sleep(gateway_info.get("session_start_limit", {}).get("max_concurrency", 1))
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        async with self.stage("cleanup"):
            await self.session.close()
            for task in tasks:
                task.cancel()
            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
            self.connections.clear()