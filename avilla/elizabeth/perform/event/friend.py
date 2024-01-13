from __future__ import annotations

from avilla.core.context import Context
from avilla.core.event import MetadataModified, ModifyDetail
from avilla.core.selector import Selector
from avilla.elizabeth.capability import ElizabethCapability
from avilla.elizabeth.collector.connection import ConnectionCollector
from avilla.standard.core.inputting import InputtingStatus
from avilla.standard.core.profile import Nick, Summary


class ElizabethEventFriendPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/elizabeth::event"
    m.identify = "friend"

    @m.entity(ElizabethCapability.event_callback, raw_event="FriendInputStatusChangedEvent")
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
        sender = raw_event["friend"]
        context._collect_metadatas(
            friend,
            Nick(sender["nickname"], sender["remark"] or sender["nickname"], None),
            Summary(sender["nickname"], "a friend contact assigned to this account"),
        )
        return MetadataModified(
            context,
            friend,
            InputtingStatus,
            {InputtingStatus.inh().value: ModifyDetail("update", raw_event["inputting"], not raw_event["inputting"])},
            operator=friend,
            scene=friend,
        )

    @m.entity(ElizabethCapability.event_callback, raw_event="FriendNickChangedEvent")
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
        sender = raw_event["friend"]
        context._collect_metadatas(
            friend,
            Nick(sender["nickname"], sender["remark"] or sender["nickname"], None),
            Summary(sender["nickname"], "a friend contact assigned to this account"),
        )
        return MetadataModified(
            context,
            friend,
            Nick,
            {Nick.inh().name: ModifyDetail("update", raw_event["to"], raw_event["from"])},
            operator=friend,
            scene=friend,
        )
