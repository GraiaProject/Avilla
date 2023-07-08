from __future__ import annotations

from typing import TYPE_CHECKING

from ...collector.connection import ConnectionCollector
from avilla.core.selector import Selector
from ...account import OneBot11Account
from avilla.core.account import AccountInfo
from ...net.ws_client import OneBot11WsClientNetworking
from avilla.standard.core.account.event import AccountRegistered, AccountAvailable, AccountUnavailable
from avilla.core.platform import Abstract, Branch, Land, Platform, Version

from ...descriptor.event import OneBot11EventParse

from loguru import logger

if TYPE_CHECKING:
    ...


class OneBot11EventLifespanPerform((m := ConnectionCollector())._):
    m.post_applying = True

    @OneBot11EventParse.collect(m, "meta_event.lifecycle.connect")
    async def connect(self, raw_event: dict):
        self_id: int = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            # TODO: land should not be hardcoded as qq
            # create account instance
            account = OneBot11Account(route=Selector().land("qq").account(str(self_id)), protocol=self.protocol)

            version_info = await self.connection.call("get_version_info")
            assert version_info is not None
            platform = Platform(
                Land("qq"),
                Abstract(f"onebot/{version_info['protocol_version']}"),
                Branch(version_info["app_name"]),
                Version({"app": version_info["app_version"]}),
            )
            # TODO: more consistent platform info

            self.connection.accounts[self_id] = account
            self.protocol.avilla.accounts[account.route] = AccountInfo(account.route, account, self.protocol, platform)

            # TODO: more networking support
            if isinstance(self.connection, OneBot11WsClientNetworking):
                account.websocket_client = self.connection
        logger.info(f"Account {self_id} connected and created")
        return AccountRegistered(self.protocol.avilla, account)

    @OneBot11EventParse.collect(m, "meta_event.lifecycle.enable")
    async def enable(self, raw_event: dict):
        self_id: int = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received enable event {raw_event}")
            return
        account.status.enabled = True
        logger.warning(f"Account {self_id} enabled by remote")
        return AccountAvailable(self.protocol.avilla, account)

    @OneBot11EventParse.collect(m, "meta_event.lifecycle.disable")
    async def disable(self, raw_event: dict):
        self_id: int = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received disable event {raw_event}")
            return
        account.status.enabled = False
        logger.warning(f"Account {self_id} disabled by remote")
        # TODO: remove registry after timeout
        return AccountUnavailable(self.protocol.avilla, account)

    @OneBot11EventParse.collect(m, "meta_event.heartbeat")
    async def heartbeat(self, raw_event: dict):
        self_id: int = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received heartbeat event {raw_event}")
            return
        logger.debug(f"Heartbeat received from account {self_id}")
