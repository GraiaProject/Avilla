from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from avilla.core.account import AccountInfo
from avilla.core.platform import Abstract, Land, Platform, Version
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.selector import Selector
from avilla.red.account import RedAccount
from avilla.red.collector.connection import ConnectionCollector
from avilla.standard.core.account.event import AccountRegistered

if TYPE_CHECKING:
    ...


class RedEventLifespanPerform((m := ConnectionCollector())._):
    m.post_applying = True

    @EventParse.collect(m, "meta::connect")
    async def connect(self, raw_event: dict):
        self_id: int = raw_event["authData"]["account"]
        account = self.connection.account
        if account is None:
            # create account instance
            account = RedAccount(route=Selector().land("qq").account(str(self_id)), protocol=self.protocol)
        else:
            account.route = Selector().land("qq").account(str(self_id))

        version_info = raw_event["version"]
        platform = Platform(
            Land("qq"),
            Abstract(f"red-protocol/{version_info}"),
            Version({"app": version_info}),
        )

        self.connection.account = account
        self.protocol.avilla.accounts[account.route] = AccountInfo(account.route, account, self.protocol, platform)
        account.websocket_client = self.connection

        logger.info(f"Account {self_id} connected and created")
        return AccountRegistered(self.protocol.avilla, account)
