from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import TYPE_CHECKING

from loguru import logger
from avilla.core.account import AccountInfo
from avilla.standard.core.account import AccountRegistered, AccountAvailable, AccountUnavailable, AccountUnregistered

from satori.client import App
from satori.account import Account
from satori.model import Event, LoginStatus

from .account import SatoriAccount
from .capability import SatoriCapability
from .const import platform
from ..core import Selector
from ..core.ryanvk.staff import Staff

if TYPE_CHECKING:
    from .protocol import SatoriProtocol


class SatoriService(App):
    id = "satori.service"

    protocol: SatoriProtocol
    _accounts: dict[str, SatoriAccount]

    def __init__(self, protocol: SatoriProtocol):
        self.protocol = protocol
        self._accounts = {}
        super().__init__()
        self.register(self.handle_event)
        self.lifecycle(self.handle_lifecycle)

    def get_staff_components(self):
        return {"protocol": self.protocol, "avilla": self.protocol.avilla}

    def get_staff_artifacts(self):
        return [self.protocol.artifacts, self.protocol.avilla.global_artifacts]

    @property
    def staff(self):
        return Staff(self.get_staff_artifacts(), self.get_staff_components())

    async def handle_event(self, account: Account, event: Event):
        async def event_parse_task(connection: Account, raw: Event):
            with suppress(NotImplementedError):
                await SatoriCapability(self.staff.ext({"connection": connection})).handle_event(raw)
                return

            logger.warning(f"received unsupported event {raw.type}: {raw}")

        asyncio.create_task(event_parse_task(account, event))

    async def handle_lifecycle(self, account: Account, state: LoginStatus):
        if state == LoginStatus.ONLINE:
            route = Selector().land(account.platform).account(account.self_id)
            _account = SatoriAccount(route, self.protocol)
            self.protocol.avilla.accounts[route] = AccountInfo(
                route, _account, self.protocol, platform(account.platform)
            )
            self.protocol.avilla.broadcast.postEvent(AccountRegistered(self.protocol.avilla, _account))
            self._accounts[account.identity] = _account
            _account.client = account
        elif state == LoginStatus.CONNECT:
            _account = self._accounts[account.identity]
            self.protocol.avilla.broadcast.postEvent(AccountAvailable(self.protocol.avilla, _account))
            _account.client = account
            _account.status.enabled = True
        elif state == LoginStatus.DISCONNECT:
            _account = self._accounts[account.identity]
            _account.status.enabled = False
            self.protocol.avilla.broadcast.postEvent(AccountUnavailable(self.protocol.avilla, _account))
        elif state == LoginStatus.OFFLINE:
            _account = self._accounts[account.identity]
            _account.status.enabled = False
            self.protocol.avilla.broadcast.postEvent(AccountUnregistered(self.protocol.avilla, _account))
            with suppress(KeyError):
                del self._accounts[account.identity]
                del self.protocol.avilla.accounts[_account.route]
