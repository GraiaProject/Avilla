from __future__ import annotations

from flywheel import scoped_collect
from loguru import logger
from satori.client.account import Account
from satori.model import Event, LoginStatus

from avilla.core.account import AccountInfo
from avilla.core.selector import Selector
from avilla.satori.account import SatoriAccount
from avilla.satori.bases import InstanceOfConnection
from avilla.satori.capability import SatoriCapability
from avilla.satori.const import platform
from avilla.standard.core.account.event import (
    AccountAvailable,
    AccountRegistered,
    AccountUnavailable,
    AccountUnregistered,
)


class SatoriEventLifespanPerform(m := scoped_collect.globals().target, InstanceOfConnection, static=True):

    @m.impl(SatoriCapability.event_callback, raw_event="login-added")
    async def connect(self, event: Event):
        self_id = event.self_id
        account = Account(event.platform, self_id, self.connection.config)
        route = Selector().land(event.platform).account(self_id)
        _account = SatoriAccount(route=route, protocol=self.protocol)
        self.protocol.service.accounts[account.identity] = account

        for conn in self.protocol.service.connections:
            if conn.config == self.connection.config:
                conn.accounts[account.identity] = account

        self.protocol.avilla.accounts[route] = AccountInfo(route, _account, self.protocol, platform(account.platform))
        self.protocol.service._accounts[account.identity] = _account
        _account.client = self.connection
        return AccountRegistered(self.protocol.avilla, _account)

    @m.impl(SatoriCapability.event_callback, raw_event="login-updated")
    async def enable(self, event: Event):
        identity = f"{event.platform}/{event.self_id}"
        account = self.protocol.service.accounts.get(identity)
        if account is None:
            logger.warning(f"Unknown account {identity} received enable event {event}")
            raise NotImplementedError
        _account = self.protocol.service._accounts[identity]
        if _account.status.enabled and event.login and event.login.status != LoginStatus.ONLINE:
            _account.status.enabled = False
            logger.warning(f"Account {identity} disabled by remote")
            account.connected.clear()
            return AccountUnavailable(self.protocol.avilla, _account)
        if not _account.status.enabled and event.login and event.login.status == LoginStatus.ONLINE:
            _account.status.enabled = True
            account.connected.set()
            logger.warning(f"Account {identity} enabled by remote")
            return AccountAvailable(self.protocol.avilla, _account)
        raise NotImplementedError

    @m.impl(SatoriCapability.event_callback, raw_event="login-removed")
    async def disable(self, event: Event):
        identity = f"{event.platform}/{event.self_id}"
        account = self.protocol.service.accounts.get(identity)
        if account is None:
            logger.warning(f"Unknown account {identity} received disable event {event}")
            raise NotImplementedError
        _account = self.protocol.service._accounts[identity]
        _account.status.enabled = False
        logger.warning(f"Account {identity} disabled by remote")
        account.connected.clear()
        del self.protocol.service.accounts[account.identity]

        for conn in self.protocol.service.connections:
            if conn.config == self.connection.config:
                del conn.accounts[account.identity]
        del self.protocol.avilla.accounts[_account.route]
        del self.protocol.service._accounts[identity]
        return AccountUnregistered(self.protocol.avilla, _account)
