from __future__ import annotations

from loguru import logger

from avilla.core.account import AccountInfo
from avilla.core.selector import Selector
from avilla.satori.account import SatoriAccount
from avilla.satori.collector.connection import ConnectionCollector
from avilla.satori.capability import SatoriCapability
from avilla.satori.const import platform
from avilla.standard.core.account.event import (
    AccountAvailable,
    AccountRegistered,
    AccountUnavailable,
    AccountUnregistered
)
from satori.model import Event, LoginStatus
from satori.account import Account


class SatoriEventLifespanPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/satori::event"
    m.identify = "lifespan"

    @m.entity(SatoriCapability.event_callback, raw_event="login-added")
    async def connect(self, raw_event: Event):
        self_id = raw_event.self_id
        account = Account(raw_event.platform, self_id, self.connection.client)
        route = Selector().land(raw_event.platform).account(self_id)
        _account = SatoriAccount(route=route, protocol=self.protocol)

        self.connection.client.accounts[account.identity] = account
        self.connection.client.app.accounts[account.identity] = account

        self.protocol.avilla.accounts[route] = AccountInfo(
                route, _account, self.protocol, platform(account.platform)
            )
        self.protocol.service._accounts[account.identity] = _account
        _account.client = self.connection
        return AccountRegistered(self.protocol.avilla, _account)

    @m.entity(SatoriCapability.event_callback, raw_event="login-updated")
    async def enable(self, raw_event: Event):
        identity = f"{raw_event.platform}/{raw_event.self_id}"
        account = self.connection.client.accounts.get(identity)
        if account is None:
            logger.warning(f"Unknown account {identity} received enable event {raw_event}")
            return
        _account = self.protocol.service._accounts[identity]
        if _account.status.enabled and raw_event.login and raw_event.login.status != LoginStatus.ONLINE:
            _account.status.enabled = False
            logger.warning(f"Account {identity} disabled by remote")
            account.connected.clear()
            return AccountUnavailable(self.protocol.avilla, _account)
        if not _account.status.enabled and raw_event.login and raw_event.login.status == LoginStatus.ONLINE:
            _account.status.enabled = True
            account.connected.set()
            logger.warning(f"Account {identity} enabled by remote")
            return AccountAvailable(self.protocol.avilla, _account)

    @m.entity(SatoriCapability.event_callback, raw_event="login-removed")
    async def disable(self, raw_event: Event):
        identity = f"{raw_event.platform}/{raw_event.self_id}"
        account = self.connection.client.accounts.get(identity)
        if account is None:
            logger.warning(f"Unknown account {identity} received disable event {raw_event}")
            return
        _account = self.protocol.service._accounts[identity]
        _account.status.enabled = False
        logger.warning(f"Account {identity} disabled by remote")
        account.connected.clear()
        del self.connection.client.accounts[identity]
        del self.connection.client.app.accounts[identity]
        del self.protocol.avilla.accounts[_account.route]
        del self.protocol.service._accounts[identity]
        return AccountUnregistered(self.protocol.avilla, _account)
