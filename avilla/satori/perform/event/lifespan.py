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
)

class SatoriEventLifespanPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/satori::event"
    m.identify = "lifespan"

    @m.entity(SatoriCapability.event_callback, event="login-added")
    async def connect(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = SatoriAccount(route=Selector().land(raw_event["platform"]).account(self_id), protocol=self.protocol)
        self.connection.accounts[self_id] = account
        self.protocol.avilla.accounts[account.route] = AccountInfo(
            account.route, account, self.protocol, platform(raw_event["platform"])
        )
        account.client = self.connection
        account.status.enabled = raw_event["login"]["status"] == 1
        logger.info(f"Account {self_id} connected and created")
        return AccountRegistered(self.protocol.avilla, account)

    @m.entity(SatoriCapability.event_callback, event="login-updated")
    async def enable(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received enable event {raw_event}")
            return
        if account.status.enabled and raw_event["login"]["status"] != 1:
            account.status.enabled = False
            logger.warning(f"Account {self_id} disabled by remote")
            return AccountUnavailable(self.protocol.avilla, account)
        elif not account.status.enabled and raw_event["login"]["status"] == 1:
            account.status.enabled = True
            logger.warning(f"Account {self_id} enabled by remote")
            return AccountAvailable(self.protocol.avilla, account)
        return

    @m.entity(SatoriCapability.event_callback, event="login-removed")
    async def disable(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received disable event {raw_event}")
            return
        account.status.enabled = False
        logger.warning(f"Account {self_id} disabled by remote")
        return AccountUnavailable(self.protocol.avilla, account)
