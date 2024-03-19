from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

from flywheel import InstanceContext
from loguru import logger
from satori.client import App
from satori.client.account import Account
from satori.model import Event, LoginStatus

from avilla.core import Selector
from avilla.core.account import AccountInfo
from avilla.standard.core.account import (
    AccountAvailable,
    AccountRegistered,
    AccountUnavailable,
    AccountUnregistered,
)

from .account import SatoriAccount
from .capability import SatoriCapability
from .const import platform

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

    async def handle_event(self, account: Account, event: Event):
        event_instance = InstanceContext()
        event_instance.instances[Account] = account
        event_instance.instances[type(self.protocol)] = self.protocol
        if account.identity in self._accounts:
            event_instance.instances[SatoriAccount] = self._accounts[account.identity]
        with event_instance.scope(), suppress(NotImplementedError):
            res = await SatoriCapability.event_callback(event)
            if isinstance(res, list):
                for e in res:
                    self.protocol.avilla.event_record(e)
                    self.protocol.post_event(e)
            else:
                self.protocol.avilla.event_record(res)
                self.protocol.post_event(res)
            return

        logger.warning(f"received unsupported event {event.type}: {event}")

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
