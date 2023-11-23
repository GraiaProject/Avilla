from __future__ import annotations

import asyncio
import json
import sys
from contextlib import suppress
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, cast

import aiohttp
from launart import Service
from launart.manager import Launart
from launart.utilles import any_completed
from loguru import logger

from avilla.core.account import AccountInfo
from avilla.core.selector import Selector
from avilla.qqapi.account import QQAPIAccount
from avilla.qqapi.const import PLATFORM
from avilla.qqapi.exception import NetworkError, UnauthorizedException
from avilla.standard.core.account import (
    AccountAvailable,
    AccountRegistered,
    AccountUnavailable,
    AccountUnregistered,
)

from .base import CallMethod, QQAPINetworking
from .util import Opcode, Payload, validate_response

if TYPE_CHECKING:
    from avilla.qqapi.protocol import QQAPIConfig, QQAPIProtocol


class QQAPIWsClientNetworking(QQAPINetworking, Service):
    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking", "cleanup"}

    config: QQAPIConfig
    connections: dict[tuple[int, int], aiohttp.ClientWebSocketResponse]
    session: aiohttp.ClientSession

    @property
    def id(self):
        return f"qqapi/connection/client#{self.config.id}"

    def __init__(self, protocol: QQAPIProtocol, config: QQAPIConfig) -> None:
        super().__init__(protocol)
        self.config = config
        if any([not config.id, not config.token, not config.secret]):
            raise ValueError("config is not complete")
        self.connections = {}

    async def get_access_token(self) -> str:
        if self._access_token is None or (
            self._expires_in and datetime.now(timezone.utc) > self._expires_in - timedelta(seconds=30)
        ):
            async with self.session.post(
                self.config.auth_base,
                json={
                    "appId": self.config.id,
                    "clientSecret": self.config.secret,
                },
            ) as resp:
                if resp.status != 200 or not resp.content:
                    raise NetworkError(
                        f"Get authorization failed with status code {resp.status}." " Please check your config."
                    )
                data = await resp.json()
            self._access_token = cast(str, data["access_token"])
            self._expires_in = datetime.now(timezone.utc) + timedelta(seconds=int(data["expires_in"]))
        return self._access_token

    async def _get_authorization_header(self) -> str:
        """获取当前 Bot 的鉴权信息"""
        if self.config.is_group_bot:
            return f"QQBot {await self.get_access_token()}"
        return f"Bot {self.config.id}.{self.config.token}"

    async def get_authorization_header(self) -> dict[str, str]:
        """获取当前 Bot 的鉴权信息"""
        headers = {"Authorization": await self._get_authorization_header()}
        if self.config.is_group_bot:
            headers["X-Union-Appid"] = self.config.id
        return headers

    async def message_receive(self, shard: tuple[int, int]):
        if (connection := self.connections.get(shard)) is None:
            raise RuntimeError("connection is not established")

        async for msg in connection:
            # logger.debug(f"{msg=}")

            if msg.type in {aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSED}:
                self.close_signal.set()
                break
            elif msg.type == aiohttp.WSMsgType.TEXT:
                data: dict = json.loads(cast(str, msg.data))
                if data["op"] == Opcode.RECONNECT:
                    logger.warning("Received reconnect event from server, will reconnect in 5 seconds...")
                    break
                if data["op"] == Opcode.INVALID_SESSION:
                    self.session_id = None
                    self.sequence = None
                    logger.warning("Received invalid session event from server, will try to resume")
                    break
                if data["op"] == Opcode.HEARTBEAT_ACK:
                    continue
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

    async def _call_http(
        self, method: CallMethod, action: str, headers: dict[str, str] | None = None, params: dict | None = None
    ) -> dict:
        params = params or {}
        params = {k: v for k, v in params.items() if v is not None}
        if method in {"get", "fetch"}:
            async with self.session.get(
                (self.config.get_api_base() / action).with_query(params),
                headers=headers,
            ) as resp:
                return await validate_response(resp)

        if method == "patch":
            async with self.session.patch(
                (self.config.get_api_base() / action),
                json=params,
                headers=headers,
            ) as resp:
                return await validate_response(resp)

        if method == "put":
            async with self.session.put(
                (self.config.get_api_base() / action),
                json=params,
                headers=headers,
            ) as resp:
                return await validate_response(resp)

        if method == "delete":
            async with self.session.delete(
                (self.config.get_api_base() / action).with_query(params),
                headers=headers,
            ) as resp:
                return await validate_response(resp)

        if method in {"post", "update"}:
            async with self.session.post(
                (self.config.get_api_base() / action),
                json=params,
                headers=headers,
            ) as resp:
                return await validate_response(resp)

        if method == "multipart":
            if params is None:
                raise TypeError("multipart requires params")
            data = aiohttp.FormData(params["data"], quote_fields=False)
            for k, v in params["files"].items():
                if isinstance(v, dict):
                    data.add_field(k, v["value"], filename=v.get("filename"), content_type=v.get("content_type"))
                else:
                    data.add_field(k, v)

            async with self.session.post(
                (self.config.get_api_base() / action),
                data=data,
                headers=headers,
            ) as resp:
                return await validate_response(resp)

        raise ValueError(f"unknown method {method}")

    async def call_http(self, method: CallMethod, action: str, params: dict | None = None) -> dict:
        headers = await self.get_authorization_header()
        try:
            return await self._call_http(method, action, headers, params)
        except UnauthorizedException as e:
            if not self.config.is_group_bot:
                raise
            self._access_token = None
            try:
                headers = await self.get_authorization_header()
            except Exception:
                raise e from None
            try:
                return await self._call_http(method, action, headers, params)
            except Exception as e1:
                raise e1 from None

    async def wait_for_available(self):
        await self.status.wait_for_available()

    def get_staff_components(self):
        return {"connection": self, "protocol": self.protocol, "avilla": self.protocol.avilla}

    def get_staff_artifacts(self):
        return [self.protocol.artifacts, self.protocol.avilla.global_artifacts]

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
            assert payload.opcode == Opcode.HELLO, f"Received unexpected payload: {payload!r}"
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
                    "token": await self._get_authorization_header(),
                    "intents": self.config.intent.to_int(),
                    "shard": list(shard),
                    "properties": {
                        "$os": sys.platform,
                        "$language": f"python {sys.version}",
                        "$sdk": "Avilla",
                    },
                },
            )
        else:
            payload = Payload(
                op=Opcode.RESUME,
                d={
                    "token": await self._get_authorization_header(),
                    "session_id": self.session_id,
                    "seq": self.sequence,
                },
            )

        try:
            await self.send(asdict(payload), shard)
        except Exception as e:
            logger.error(f"Error while sending {payload.opcode.name.title()} event: {e}")
            return False

        if not self.session_id:
            # https://bot.q.qq.com/wiki/develop/api/gateway/reference.html#_2-%E9%89%B4%E6%9D%83%E8%BF%9E%E6%8E%A5
            # 鉴权成功之后，后台会下发一个 Ready Event
            payload = Payload(**await connection.receive_json())
            if payload.opcode == Opcode.INVALID_SESSION:
                logger.warning("Received invalid session event from server, will try to resume")
                return False
            if not (payload.opcode == Opcode.DISPATCH and payload.type == "READY" and payload.data):
                logger.error(f"Received unexpected payload: {payload}")
                return False
            self.sequence = payload.sequence
            self.session_id = payload.data["session_id"]
            self.self_info = payload.data["user"]
            self.account_id = payload.data["user"]["id"]
            account_route = Selector().land("qq").account(self.account_id)
            if account_route in self.protocol.avilla.accounts:
                account = cast(QQAPIAccount, self.protocol.avilla.accounts[account_route].account)
            else:
                account = QQAPIAccount(account_route, self.protocol)
                self.protocol.avilla.accounts[account_route] = AccountInfo(
                    account_route,
                    account,
                    self.protocol,
                    PLATFORM,
                )
            self.protocol.service.accounts[self.account_id] = account
            account.connection = self
            self.protocol.avilla.broadcast.postEvent(AccountRegistered(self.protocol.avilla, account))
        else:
            account = self.protocol.service.accounts[self.account_id]
            account.connection = self
        self.protocol.avilla.broadcast.postEvent(AccountAvailable(self.protocol.avilla, account))
        return True

    async def _heartbeat(self, heartbeat_interval: int, shard: tuple[int, int]):
        """心跳"""
        while True:
            if self.session_id:
                with suppress(Exception):
                    await self.send({"op": 1, "d": self.sequence}, shard=shard)
            await asyncio.sleep(heartbeat_interval / 1000)

    async def connection_daemon(
        self, manager: Launart, session: aiohttp.ClientSession, url: str, shard: tuple[int, int]
    ):
        while not manager.status.exiting:
            try:
                async with session.ws_connect(url, timeout=30) as conn:
                    self.connections[shard] = conn
                    logger.info(f"{self.id} Websocket client connected")
                    heartbeat_interval = await self._hello(shard)
                    if not heartbeat_interval:
                        await asyncio.sleep(3)
                        continue
                    result = await self._authenticate(shard)
                    if not result:
                        await asyncio.sleep(3)
                        continue
                    account_route = Selector().land("qq").account(self.account_id)
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
                        receiver_task.cancel()
                        heartbeat_task.cancel()
                        with suppress(KeyError):
                            del self.connections[shard]
                            await self.protocol.avilla.broadcast.postEvent(
                                AccountUnregistered(
                                    self.protocol.avilla, self.protocol.avilla.accounts[account_route].account
                                )
                            )
                            del self.protocol.service.accounts[self.account_id]
                            del self.protocol.avilla.accounts[account_route]
                        return
                    if close_task in done:
                        receiver_task.cancel()
                        heartbeat_task.cancel()
                        logger.warning(f"{self} Connection closed by server, will reconnect in 5 seconds...")

                        with suppress(KeyError):
                            await self.protocol.avilla.broadcast.postEvent(
                                AccountUnavailable(
                                    self.protocol.avilla, self.protocol.avilla.accounts[account_route].account
                                )
                            )
                            del self.protocol.service.accounts[self.account_id]
                            # del self.protocol.avilla.accounts[account_route]
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
            gateway_info = await self.call_http("get", "gateway/bot")
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
                logger.debug(f"Get Shards: {shards}")
                for i in range(shards):
                    tasks.append(
                        asyncio.create_task(self.connection_daemon(manager, self.session, ws_url, (i, shards)))
                    )
                    await asyncio.sleep(gateway_info.get("session_start_limit", {}).get("max_concurrency", 1))
            await any_completed(*tasks)

        async with self.stage("cleanup"):
            await self.session.close()
            for task in tasks:
                task.cancel()
            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
            self.connections.clear()
