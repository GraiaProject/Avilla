from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, cast

from launart import Launart, Service, any_completed
from loguru import logger
from telegram import Message
from telegram.error import InvalidToken as InvalidTokenOrigin
from telegram.error import NetworkError, TimedOut
from telegram.ext import ExtBot

from avilla.core import Selector
from avilla.core.account import AccountInfo
from avilla.standard.core.account import (
    AccountAvailable,
    AccountRegistered,
    AccountUnregistered,
)
from avilla.telegram.account import TelegramAccount
from avilla.telegram.bot.base import TelegramBase
from avilla.telegram.const import PLATFORM
from avilla.telegram.exception import InvalidToken
from avilla.telegram.fragments import MessageFragment

if TYPE_CHECKING:
    from avilla.telegram.protocol import TelegramBotConfig, TelegramProtocol


class TelegramBot(TelegramBase, Service):
    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking"}

    protocol: TelegramProtocol
    config: TelegramBotConfig

    bot: ExtBot
    available: bool
    __auth: bool
    __offset: int | None

    def __init__(self, protocol: TelegramProtocol, config: TelegramBotConfig):
        super().__init__(protocol)
        self.protocol = protocol
        self.config = config
        self.__offset = None
        self.__auth = False

    @property
    def available(self):
        return self.__auth and not self.kill_switch.is_set() and not self.timeout_signal.is_set()

    @property
    def account_id(self):
        return int(self.config.token.split(":")[0])

    @property
    def id(self):
        return f"telegram/bot#{self.account_id}"

    async def auth(self, __retries: int = 0, __max_retries: int = 5):
        try:
            self.bot = ExtBot(
                self.config.token, base_url=str(self.config.base_url), base_file_url=str(self.config.base_file_url)
            )
            await self.bot.initialize()
            logger.info(f"{self.id} is available")
            self.__auth = True
        except InvalidTokenOrigin as e:
            raise InvalidToken(self.config.token) from e
        except (TimedOut, NetworkError) as e:
            logger.warning(f"Failed to connect to telegram server: {e}, retrying ({__retries}/{__max_retries})...")
            if __retries < __max_retries:
                await self.auth(__retries + 1, __max_retries)
            else:
                logger.error(f"Failed to connect to telegram server: {e}, aborting...")

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

    async def message_receive(self):
        while not self.manager.status.exiting:
            try:
                if not (update := await self.bot.get_updates(offset=self.__offset, timeout=self.config.timeout)):
                    continue
                for u in update:
                    yield self, u
                self.__offset = update[-1].update_id + 1
            except InvalidToken:
                self.kill_switch.set()
                break
            except (TimedOut, TimeoutError, NetworkError):
                self.timeout_signal.set()
                break

    async def send(self, target, fragments):
        if self.config.reformat:
            fragments = MessageFragment.sort(*fragments)
        fragments = MessageFragment.compose(*fragments)
        chat = int(target.pattern["chat"])
        thread = target.pattern.get("thread", None)
        thread = int(thread) if thread else None
        sent_ids = []
        for fragment in fragments:
            msg = await fragment.send(self.bot, chat, thread=thread)
            if isinstance(msg, Message):
                sent_ids.append(msg.message_id)
            else:
                sent_ids.extend([m.message_id for m in msg])

        return sent_ids

    async def wait_for_available(self):
        await self.status.wait_for_available()

    def get_staff_components(self):
        return {"instance": self, "protocol": self.protocol, "avilla": self.protocol.avilla, "account": self.account}

    def __staff_generic__(self, element_type: dict, event_type: dict):
        ...

    def get_staff_artifacts(self):
        return [self.protocol.artifacts, self.protocol.avilla.global_artifacts]

    async def unregister(self):
        avilla = self.protocol.avilla
        for n in list(avilla.accounts.keys()):
            logger.debug(f"Unregistering telegram account {n}...")
            await avilla.broadcast.postEvent(AccountUnregistered(avilla, avilla.accounts[n].account))
            if n.follows("land(telegram).account") and n["account"] == str(self.account_id):
                del avilla.accounts[n]

    async def daemon(self):
        while not self.manager.status.exiting:
            self.timeout_signal.clear()
            timeout_task = asyncio.create_task(self.timeout_signal.wait())
            receiver_task = asyncio.create_task(self.message_handle())
            kill_task = asyncio.create_task(self.kill_switch.wait())
            sigexit_task = asyncio.create_task(self.manager.status.wait_for_sigexit())

            done, pending = await any_completed(
                sigexit_task,
                timeout_task,
                kill_task,
                receiver_task,
            )

            if kill_task in done or sigexit_task in done:
                receiver_task.cancel()
                if kill_task in done:
                    logger.warning(f"Token for {self.id} is invalid, will not reconnect")
                else:
                    logger.info(f"{self.id} exiting...")
                await self.unregister()
                return
            if timeout_task in done:
                receiver_task.cancel()
                logger.warning(f"Timeout for {self.id}, will reconnect in 5 seconds...")
                await asyncio.sleep(5)

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            await self.auth()
            self.register()

        async with self.stage("blocking"):
            await any_completed(manager.status.wait_for_sigexit(), self.daemon())
