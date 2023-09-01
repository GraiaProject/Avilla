from __future__ import annotations
import asyncio

from dataclasses import dataclass

from typing import cast
from launart import Service, Launart, any_completed
from loguru import logger
from telegram.ext import ExtBot
from telegram.error import InvalidToken as InvalidTokenOrigin
from yarl import URL

from avilla.core.account import AccountInfo
from avilla.core.selector import Selector
from avilla.telegram.account import TelegramAccount
from avilla.elizabeth.const import PLATFORM
from avilla.standard.core.account import AccountRegistered, AccountUnregistered, AccountAvailable, AccountUnavailable
from avilla.telegram.protocol import TelegramProtocol
from avilla.telegram.exception import InvalidToken


@dataclass
class TelegramBotConfig:
    token: str
    base_url: URL = URL("https://api.telegram.org/bot")
    base_file_url: URL = URL("https://api.telegram.org/file/bot")

    timeout: int = 15
    """
    Timeout for long polling. Defaults to 15.
    Only change to 0 when testing.
    """


class TelegramBot(Service):
    required: set[str] = set()
    stages: set[str] = {"blocking"}

    protocol: TelegramProtocol
    config: TelegramBotConfig

    bot: ExtBot
    available: bool
    __offset: int | None

    def __init__(self, protocol: TelegramProtocol, config: TelegramBotConfig):
        super().__init__()
        self.protocol = protocol
        self.config = config
        self.__offset = None
        self.available = False

    @property
    def account_id(self):
        return self.config.token.split(":")[0]

    @property
    def id(self):
        return f"telegram/bot#{self.account_id}"

    async def auth(self):
        try:
            self.bot = ExtBot(
                self.config.token, base_url=str(self.config.base_url), base_file_url=str(self.config.base_file_url)
            )
            await self.bot.initialize()
            logger.info(f"{self.id} is available")
            self.available = True
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
                self.protocol.avilla.broadcast.postEvent(AccountRegistered(
                    self.protocol.avilla, account
                ))

            self.protocol.service.instance_map[self.account_id] = self
            self.protocol.avilla.broadcast.postEvent(AccountAvailable(
                self.protocol.avilla, account
            ))
        except InvalidTokenOrigin as e:
            self.available = False
            raise InvalidToken(self.config.token) from e

    async def daemon(self, manager: Launart):
        while not manager.status.exiting:
            try:
                if not self.available:
                    await self.auth()
                if not (update := await self.bot.get_updates(offset=self.__offset, timeout=self.config.timeout)):
                    continue
                for u in update:
                    logger.info(f"Rcvd update: {u.message}")
                self.__offset = update[-1].update_id + 1
            except InvalidToken:
                logger.warning(f'Invalid token for "{self.id}"')
                return
    async def launch(self, manager: Launart):
        async with self.stage("blocking"):
            await any_completed(manager.status.wait_for_sigexit(), self.daemon(manager))
