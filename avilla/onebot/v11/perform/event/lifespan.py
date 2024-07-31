from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from avilla.core.account import AccountInfo
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.selector import Selector
from avilla.onebot.v11.account import OneBot11Account
from avilla.onebot.v11.capability import OneBot11Capability
from avilla.onebot.v11.collector.connection import ConnectionCollector
from avilla.standard.core.account.event import (
    AccountAvailable,
    AccountRegistered,
    AccountUnavailable,
)

if TYPE_CHECKING:
    ...


class OneBot11EventLifespanPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/onebot11::event"
    m.identify = "lifespan"

    @m.entity(OneBot11Capability.event_callback, raw_event="meta_event.lifecycle.connect")
    async def connect(self, raw_event: dict):
        self_id: int = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            # create account instance
            account = OneBot11Account(route=Selector().land("qq").account(str(self_id)), protocol=self.protocol)
        else:
            account.route = Selector().land("qq").account(str(self_id))

        account.connection = self.connection
        platform = Platform(Land("qq"), Abstract("onebot/v11"))
        # TODO: more consistent platform info

        self.connection.accounts[self_id] = account
        self.protocol.avilla.accounts[account.route] = AccountInfo(account.route, account, self.protocol, platform)

        logger.info(f"Account {self_id} connected and created")
        return AccountRegistered(self.protocol.avilla, account)

    @m.entity(OneBot11Capability.event_callback, raw_event="meta_event.lifecycle.enable")
    async def enable(self, raw_event: dict):
        self_id: int = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received enable event {raw_event}")
            return
        account.status.enabled = True
        logger.warning(f"Account {self_id} enabled by remote")
        return AccountAvailable(self.protocol.avilla, account)

    @m.entity(OneBot11Capability.event_callback, raw_event="meta_event.lifecycle.disable")
    async def disable(self, raw_event: dict):
        self_id: int = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received disable event {raw_event}")
            return
        account.status.enabled = False
        logger.warning(f"Account {self_id} disabled by remote")
        # TODO: remove registry after timeout
        # 直接移交给网络层处理。
        return AccountUnavailable(self.protocol.avilla, account)

    @m.entity(OneBot11Capability.event_callback, raw_event="meta_event.heartbeat")
    async def heartbeat(self, raw_event: dict):
        self_id: int = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            return await self.connect(raw_event)
        logger.trace(f"Heartbeat received from account {self_id}")
