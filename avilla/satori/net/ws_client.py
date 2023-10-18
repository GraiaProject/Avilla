from __future__ import annotations

import asyncio
import json
from contextlib import suppress
from typing import TYPE_CHECKING, cast

import aiohttp
from launart import Service
from launart.manager import Launart
from launart.utilles import any_completed
from loguru import logger

from avilla.core import Selector
from avilla.core.account import AccountInfo
from avilla.satori.account import SatoriAccount
from avilla.satori.const import platform
from avilla.standard.core.account import AccountUnregistered, AccountRegistered, AccountAvailable

from .base import SatoriNetworking

if TYPE_CHECKING:
    from avilla.satori.protocol import SatoriConfig, SatoriProtocol


class SatoriWsClientNetworking(SatoriNetworking, Service):
    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking", "cleanup"}

    config: SatoriConfig
    connection: aiohttp.ClientWebSocketResponse | None = None
    session: aiohttp.ClientSession

    def __init__(self, protocol: SatoriProtocol, config: SatoriConfig) -> None:
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
                if data["op"] == 0:
                    yield self, data["body"]
                elif data["op"] > 4:
                    logger.warning(f"Received unknown event: {data}")
        else:
            await self.connection_closed()

    async def send(self, payload: dict):
        if self.connection is None:
            raise RuntimeError("connection is not established")

        await self.connection.send_json(payload)

    async def call_http(
        self,
        action: str,
        account: Selector,
        params: dict | None = None
    ) -> dict:
        ...
        endpoint = self.config.http_url / "v1" / action
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.access_token or ''}",
            "X-Platform": account["land"],
            "X-Self-ID:": account['account'],
        }
        async with self.session.post(
            endpoint,
            json=params or {},
            headers=headers,
        ) as resp:
            resp.raise_for_status()
            return json.loads(content) if (content := await resp.text()) else {}

    async def wait_for_available(self):
        await self.status.wait_for_available()

    @property
    def alive(self):
        return self.connection is not None and not self.connection.closed

    async def _authenticate(self):
        """鉴权连接"""
        if not self.connection:
            raise RuntimeError("connection is not established")
        payload = {
            "op": 3,
            "body": {
                "token": self.config.access_token,
            }
        }
        if self.sequence > -1:
            payload["body"]["sequence"] = self.sequence
        try:
            await self.send(payload)
        except Exception as e:
            logger.error(f"Error while sending IDENTIFY event: {e}")
            return False

        resp = await self.connection.receive()
        if resp.type != aiohttp.WSMsgType.TEXT:
            logger.error(f"Received unexpected payload: {resp}")
            return False
        data = resp.json()
        if data["op"] != 4:
            logger.error(f"Received unexpected payload: {data}")
            return False
        for login in data["body"]["logins"]:
            if "self_id" not in login:
                continue
            account_route = Selector().land(login.get("platform", "satori")).account(login["self_id"])
            if account_route in self.protocol.avilla.accounts:
                account = cast(SatoriAccount, self.protocol.avilla.accounts[account_route].account)
                account.status.enabled = login["status"] == 1
                account.client = self
            else:
                account = SatoriAccount(account_route, self.protocol)
                self.protocol.avilla.accounts[account_route] = AccountInfo(
                    account_route,
                    account,
                    self.protocol,
                    platform(login.get("platform", "satori")),
                )
                logger.info(f"account registered: {account_route}")
                account.status.enabled = login["status"] == 1
                account.client = self
                self.accounts[login["self_id"]] = account
                self.protocol.avilla.broadcast.postEvent(AccountRegistered(self.protocol.avilla, account))
            self.protocol.avilla.broadcast.postEvent(AccountAvailable(self.protocol.avilla, account))
        if not self.accounts:
            logger.warning(f"No account available")
            return False
        return True

    async def _heartbeat(self):
        """心跳"""
        while True:
            if self.sequence:
                with suppress(Exception):
                    await self.send({"op": 1})
            await asyncio.sleep(9)

    async def connection_daemon(self, manager: Launart, session: aiohttp.ClientSession):
        avilla = self.protocol.avilla
        while not manager.status.exiting:
            try:
                async with session.ws_connect(
                    self.config.ws_url / "v1" / "events",
                ) as self.connection:
                    logger.debug(f"{self} Websocket client connected")
                    self.close_signal.clear()
                    result = await self._authenticate()
                    if not result:
                        await asyncio.sleep(3)
                        continue
                    self.close_signal.clear()
                    close_task = asyncio.create_task(self.close_signal.wait())
                    receiver_task = asyncio.create_task(self.message_handle())
                    sigexit_task = asyncio.create_task(manager.status.wait_for_sigexit())
                    heartbeat_task = asyncio.create_task(self._heartbeat())
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
                        for v in list(avilla.accounts.values()):
                            if v.protocol is self.protocol:
                                _account = v.route["account"]
                                if _account in self.accounts:
                                    del self.accounts[_account]
                        return
                    if close_task in done:
                        receiver_task.cancel()
                        logger.warning(f"{self} Connection closed by server, will reconnect in 5 seconds...")
                        accounts = {str(i) for i in self.accounts.keys()}
                        for n in list(avilla.accounts.keys()):
                            logger.debug(f"Unregistering satori account {n}...")
                            account = cast("SatoriAccount", avilla.accounts[n].account)
                            account.status.enabled = False
                            await avilla.broadcast.postEvent(AccountUnregistered(avilla, account))
                            if n["account"] in accounts:
                                del avilla.accounts[n]
                        self.accounts.clear()
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
