from __future__ import annotations

from loguru import logger

from avilla.core.account import AccountInfo
from avilla.core.platform import Abstract, Land, Platform, Version
from avilla.core.selector import Selector
from avilla.red.account import RedAccount
from avilla.red.capability import RedCapability
from avilla.red.collector.connection import ConnectionCollector
from avilla.standard.core.account.event import AccountRegistered, AccountAvailable


class RedEventLifespanPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/red::event"
    m.identify = "lifespan"

    @m.entity(RedCapability.event_callback, event_type="meta::connect")
    async def connect(self,  event_type: ..., raw_event: dict):
        self_id: int = raw_event["authData"]["account"]
        account = self.connection.account

        if account is None:
            # create account instance
            account = RedAccount(route=Selector().land("qq").account(str(self_id)), protocol=self.protocol)
            version_info = raw_event["version"]
            platform = Platform(
                Land("qq"),
                Abstract(f"red-protocol/{version_info}"),
                Version({"app": version_info}),
            )
            self.connection.account = account
            self.protocol.avilla.accounts[account.route] = AccountInfo(account.route, account, self.protocol, platform)
            account.websocket_client = self.connection
            logger.success(f"Account {self_id} connected and created with red-protocol version {version_info}")
            return AccountRegistered(self.protocol.avilla, account)
        else:
            self.connection.account = account
            account.route = Selector().land("qq").account(str(self_id))
            return AccountAvailable(self.protocol.avilla, account)
