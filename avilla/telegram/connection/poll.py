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
    def id(self):
        return f"telegram/connection/poll#{self.account_id}"

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

    async def wait_for_available(self):
        await self.status.wait_for_available()

    def get_staff_components(self):
        return {"connection": self, "protocol": self.protocol, "avilla": self.protocol.avilla, "account": self.account}

    def __staff_generic__(self, element_type: dict, event_type: dict):
        ...

    def get_staff_artifacts(self):
        return [self.protocol.artifacts, self.protocol.avilla.global_artifacts]

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            self.session = ClientSession()
            self.__offset = None
            self.register()
            await self.staff.call_fn(PreferenceCapability.delete_webhook)
            self.__alive = True

        async with self.stage("blocking"):
            await any_completed(manager.status.wait_for_sigexit(), self.daemon())
