from __future__ import annotations

from dataclasses import dataclass

from launart import Service, Launart, any_completed
from loguru import logger
from telegram.ext import ExtBot
from yarl import URL

from avilla.telegram.protocol import TelegramProtocol


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
    __offset: int | None

    def __init__(self, protocol: TelegramProtocol, config: TelegramBotConfig):
        super().__init__()
        self.protocol = protocol
        self.config = config
        self.bot = ExtBot(
            self.config.token, base_url=str(self.config.base_url), base_file_url=str(self.config.base_file_url)
        )
        self.__offset = None

    @property
    def account_id(self):
        return self.config.token.split(":")[0]

    @property
    def id(self):
        return f"telegram/bot#{self.account_id}"

    async def daemon(self, manager: Launart):
        await self.bot.initialize()
        while not manager.status.exiting:
            update = await self.bot.get_updates(offset=self.__offset, timeout=self.config.timeout)
            if not update:
                continue
            for u in update:
                logger.info(f"Rcvd update: {u.message}")
            self.__offset = update[-1].update_id + 1

    async def launch(self, manager: Launart):
        async with self.stage("blocking"):
            await any_completed(manager.status.wait_for_sigexit(), self.daemon(manager))
