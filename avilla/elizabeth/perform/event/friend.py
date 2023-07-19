from __future__ import annotations

from avilla.core.context import Context
from avilla.core.event import MetadataModified, ModifyDetail
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.selector import Selector
from avilla.elizabeth.collector.connection import ConnectionCollector
from avilla.standard.core.inputting import InputtingStatus
from avilla.standard.core.profile import Nick


class ElizabethEventFriendPerform((m := ConnectionCollector())._):
    m.post_applying = True

    @EventParse.collect(m, "FriendInputStatusChangedEvent")
    async def friend_input_status_changed(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        friend = land.friend(str(raw_event["friend"]["id"]))
        context = Context(
            account,
            friend,
            friend,
            friend,
            account_route,
        )
        return MetadataModified(
            context,
            friend,
            InputtingStatus,
            {
                InputtingStatus.inh(lambda x: x.value): ModifyDetail(
                    "update", raw_event["inputting"], not raw_event["inputting"]
                )
            },
            operator=friend,
            scene=friend,
        )

    @EventParse.collect(m, "FriendNickChangedEvent")
    async def friend_nick_changed(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        friend = land.friend(str(raw_event["friend"]["id"]))
        context = Context(
            account,
            friend,
            friend,
            friend,
            account_route,
        )
        return MetadataModified(
            context,
            friend,
            Nick,
            {Nick.inh(lambda x: x.name): ModifyDetail("update", raw_event["to"], raw_event["from"])},
            operator=friend,
            scene=friend,
        )
