from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, cast

from aiohttp import ClientSession
from launart import Launart, Service, any_completed
from loguru import logger
from yarl import URL

from avilla.core import Selector
from avilla.core.account import AccountInfo
from avilla.standard.core.account import (
    AccountAvailable,
    AccountRegistered,
    AccountUnregistered,
)
from avilla.standard.telegram.preference.capability import PreferenceCapability
from avilla.telegram.account import TelegramAccount
from avilla.telegram.connection.base import TelegramNetworking
from avilla.telegram.const import PLATFORM
from avilla.telegram.exception import InvalidToken

if TYPE_CHECKING:
    from avilla.telegram.protocol import TelegramLongPollingConfig, TelegramProtocol


class TelegramLongPollingNetworking(TelegramNetworking, Service):
    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking"}

    protocol: TelegramProtocol
    config: TelegramLongPollingConfig

    __alive: bool
    __offset: int | None

    def __init__(self, protocol: TelegramProtocol, config: TelegramLongPollingConfig):
        super().__init__(protocol)
        self.protocol = protocol
        self.config = config

    @property
    def alive(self) -> bool:
        return self.__alive

    @property
    def account_id(self):
        return int(self.config.token.split(":")[0])

    @property
    def id(self):
        return f"telegram/connection/poll#{self.account_id}"

    def register(self):
        account_route = Selector().land("telegram").account(str(self.account_id))
        if account_route in self.protocol.avilla.accounts:
            account = cast(TelegramAccount, self.protocol.avilla.accounts[account_route].account)
        else:
            account = TelegramAccount(account_route, self.protocol.avilla, self.protocol)
            self.protocol.avilla.accounts[account_route] = AccountInfo(
                account_route,
                account,
                self.protocol,
                PLATFORM,
            )
            self.protocol.avilla.broadcast.postEvent(AccountRegistered(self.protocol.avilla, account))

        self.account = account
        self.protocol.avilla.broadcast.postEvent(AccountAvailable(self.protocol.avilla, account))

    async def unregister(self):
        avilla = self.protocol.avilla
        for n in list(avilla.accounts.keys()):
            if n.follows("land(telegram).account") and n["account"] == str(self.account_id):
                logger.debug(f"unregistering telegram account {n}...")
                await avilla.broadcast.postEvent(AccountUnregistered(avilla, avilla.accounts[n].account))
                del avilla.accounts[n]

    async def message_receive(self):
        while not self.manager.status.exiting:
            logger.debug(f"polling for update, current offset: {self.__offset}...")
            try:
                updates = (await self.call("getUpdates", offset=self.__offset, timeout=30))["result"]
                if self.__offset is not None:
                    for update in updates:
                        self.__offset = update["update_id"] + 1
                        yield self, update
                elif updates:
                    self.__offset = updates[0]["update_id"]
            except InvalidToken:
                raise
            except Exception as err:
                logger.error(f"{self} failed to get updates: {err}")

    async def send(self, action: str, **kwargs) -> dict:
        async with self.session.post(
            self.config.base_url / f"bot{self.config.token}" / action, proxy=self.config.proxy, **kwargs
        ) as resp:
            return await resp.json()

    async def wait_for_available(self):
        await self.status.wait_for_available()

    def get_staff_components(self):
        return {"connection": self, "protocol": self.protocol, "avilla": self.protocol.avilla, "account": self.account}

    def __staff_generic__(self, element_type: dict, event_type: dict):
        ...

    def get_staff_artifacts(self):
        return [self.protocol.artifacts, self.protocol.avilla.global_artifacts]

    async def daemon(self):
        while not self.manager.status.exiting:
            receiver_task = asyncio.create_task(self.message_handle())
            sigexit_task = asyncio.create_task(self.manager.status.wait_for_sigexit())

            done, pending = await any_completed(
                sigexit_task,
                receiver_task,
            )

            if sigexit_task in done:
                receiver_task.cancel()
                logger.info(f"{self.id} exiting...")
                await self.unregister()
                return

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            self.session = ClientSession()
            self.__offset = None
            self.register()
            await self.staff.call_fn(PreferenceCapability.delete_webhook)
            self.__alive = True

        async with self.stage("blocking"):
            await any_completed(manager.status.wait_for_sigexit(), self.daemon())
