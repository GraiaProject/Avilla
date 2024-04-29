from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, AsyncIterator, cast

import aiohttp
from aiohttp import ClientSession
from launart import Launart, any_completed
from loguru import logger
from typing_extensions import Self

from avilla.core import Selector
from avilla.core.account import AccountInfo
from avilla.core.ryanvk.staff import Staff
from avilla.standard.core.account import (
    AccountAvailable,
    AccountRegistered,
    AccountUnregistered,
)
from avilla.telegram.account import TelegramAccount
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.connection.util import validate_response
from avilla.telegram.const import PLATFORM

if TYPE_CHECKING:
    from avilla.telegram.protocol import (  # noqa
        TelegramLongPollingConfig,
        TelegramProtocol,
        TelegramWebhookConfig,
    )


class TelegramNetworking:
    account: TelegramAccount | None
    config: TelegramLongPollingConfig | TelegramWebhookConfig
    protocol: TelegramProtocol
    session: ClientSession

    if TYPE_CHECKING:
        id: str
        manager: Launart

    @property
    def account_id(self) -> int:
        return int(self.config.token.split(":")[0])

    def __init__(self, protocol: TelegramProtocol):
        super().__init__()
        self.account = None
        self.protocol = protocol

    def get_staff_components(self):
        return {"connection": self, "protocol": self.protocol, "avilla": self.protocol.avilla}

    def get_staff_artifacts(self):
        return [self.protocol.artifacts, self.protocol.avilla.global_artifacts]

    @property
    def staff(self):
        return Staff(self.get_staff_artifacts(), self.get_staff_components())

    def message_receive(self) -> AsyncIterator[tuple[Self, dict]]: ...

    @property
    def alive(self) -> bool:  # noqa
        ...

    async def wait_for_available(self): ...

    async def send(self, action: str, **kwargs) -> dict:
        async with self.session.post(
            self.config.base_url / f"bot{self.config.token}" / action, proxy=self.config.proxy, **kwargs
        ) as resp:
            return await resp.json()

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

    async def message_handle(self):
        async for connection, data in self.message_receive():
            logger.debug(f"{data = }")

            async def process_media_group():
                # TODO: re-implement process_media_group
                pass

            async def event_parse_task():
                await TelegramCapability(connection.staff).handle_event(list(data.keys())[-1], data)

            asyncio.create_task(event_parse_task())  # noqa

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

    async def call(self, _action: str, _file: dict[str, tuple[str, bytes]] | None = None, **data) -> dict:
        data = {k: v for k, v in data.items() if v is not None}

        logger.debug(f"calling {_action!r}")

        if _file:
            files = aiohttp.FormData()
            for filename, payload in _file.values():
                files.add_field(filename, payload, filename=filename)
            response = await self.send(_action, data=files, params=data)
        else:
            response = await self.send(_action, json=data)

        validate_response(response)
        logger.debug(f"call {_action!r} success")

        return response
