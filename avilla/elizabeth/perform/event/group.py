from __future__ import annotations

from datetime import timedelta

from avilla.core.context import Context
from avilla.core.event import MetadataModified, ModifyDetail
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.selector import Selector
from avilla.elizabeth.collector.connection import ConnectionCollector
from avilla.elizabeth.const import PRIVILEGE_LEVEL
from avilla.standard.core.privilege import MuteInfo, Privilege
from avilla.standard.core.profile import Summary


class ElizabethEventGroupPerform((m := ConnectionCollector())._):
    m.post_applying = True

    @EventParse.collect(m, "BotGroupPermissionChangeEvent")
    async def bot_group_permission_change(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["group"]["id"]))
        context = Context(
            account,
            group,
            group.member(str(account_route["account"])),
            group,
            group.member(str(account_route["account"])),
        )
        available = PRIVILEGE_LEVEL[raw_event["current"]] > PRIVILEGE_LEVEL[raw_event["origin"]]
        return MetadataModified(
            context,
            group.member(str(account_route["account"])),
            Privilege,
            {
                Privilege.inh(lambda x: x.available): ModifyDetail("update", available, not available),
                Privilege.inh(lambda x: x.effective): ModifyDetail("update", available, not available),
            },
            scene=group,
        )

    @EventParse.collect(m, "BotMuteEvent")
    async def bot_mute(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["operator"]["group"]["id"]))
        operator = group.member(str(raw_event["operator"]["id"]))
        context = Context(
            account,
            operator,
            group.member(str(account_route["account"])),
            group,
            group.member(str(account_route["account"])),
        )
        return MetadataModified(
            context,
            group.member(str(account_route["account"])),
            MuteInfo,
            {
                MuteInfo.inh(lambda x: x.muted): ModifyDetail("update", True, False),
                MuteInfo.inh(lambda x: x.duration): ModifyDetail("set", timedelta(raw_event["durationSeconds"]), None),
            },
            operator=operator,
            scene=group,
        )

    @EventParse.collect(m, "BotUnmuteEvent")
    async def bot_unmute(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["operator"]["group"]["id"]))
        operator = group.member(str(raw_event["operator"]["id"]))
        context = Context(
            account,
            operator,
            group.member(str(account_route["account"])),
            group,
            group.member(str(account_route["account"])),
        )
        return MetadataModified(
            context,
            group.member(str(account_route["account"])),
            MuteInfo,
            {
                MuteInfo.inh(lambda x: x.muted): ModifyDetail("update", False, True),
                MuteInfo.inh(lambda x: x.duration): ModifyDetail("clear", None, timedelta(0)),
            },
            operator=operator,
            scene=group,
        )

    @EventParse.collect(m, "GroupNameChangeEvent")
    async def group_name_change(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["group"]["id"]))
        operator = group.member(str(raw_event["operator"]["id"]))
        context = Context(
            account,
            operator,
            group,
            group,
            group.member(str(account_route["account"])),
        )
        return MetadataModified(
            context,
            group,
            Summary,
            {Summary.inh(lambda x: x.name): ModifyDetail("update", raw_event["current"], raw_event["origin"])},
            operator=operator,
            scene=group,
        )

    @EventParse.collect(m, "GroupMuteAllEvent")
    async def group_mute_all(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["group"]["id"]))
        operator = group.member(str(raw_event["operator"]["id"])) if raw_event.get("operator") else None
        context = Context(
            account,
            operator or group.member(str(account_route["account"])),  # bot self if no operator
            group,
            group,
            group.member(str(account_route["account"])),
        )
        return MetadataModified(
            context,
            group,
            MuteInfo,
            {
                MuteInfo.inh(lambda x: x.muted): ModifyDetail("update", raw_event["current"], raw_event["origin"]),
            },
            operator=operator or group.member(str(account_route["account"])),  # bot self if no operator
            scene=group,
        )

    # TODO: GroupEntranceAnnouncementChangeEvent
    # TODO: GroupAllowAnonymousChatEvent
    # TODO: GroupAllowConfessTalkEvent
    # TODO: GroupAllowMemberInviteEvent
