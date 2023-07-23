from __future__ import annotations

from datetime import timedelta
from typing import cast

from avilla.core.context import Context
from avilla.core.event import MetadataModified, ModifyDetail
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.selector import Selector
from avilla.elizabeth.collector.connection import ConnectionCollector
from avilla.elizabeth.const import PRIVILEGE_LEVEL
from avilla.standard.core.privilege import MuteInfo, Privilege
from avilla.standard.core.profile import Nick
from avilla.standard.qq.honor import Honor


class ElizabethEventGroupMemberPerform((m := ConnectionCollector())._):
    m.post_applying = True

    @EventParse.collect(m, "MemberCardChangeEvent")
    async def member_card_change(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["member"]["group"]["id"]))
        member = group.member(str(raw_event["member"]["id"]))
        operator = group.member(str(raw_event["operator"]["id"])) if raw_event.get("operator") else None
        context = Context(
            account,
            operator or group.member(account_route["account"]),
            member,
            group,
            group.member(account_route["account"]),
        )
        return MetadataModified(
            context,
            member,
            Nick,
            {Nick.inh(lambda x: x.nickname): ModifyDetail("update", raw_event["current"], raw_event["origin"])},
            operator=operator or group.member(account_route["account"]),
            scene=group,
        )

    @EventParse.collect(m, "MemberSpecialTitleChangeEvent")
    async def member_special_title_change(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["member"]["group"]["id"]))
        member = group.member(str(raw_event["member"]["id"]))
        members = await self.connection.call("fetch", "memberList", {"target": raw_event["group"]["id"]})
        members = cast("list[dict]", members)
        operator_id = next((d["id"] for d in members if d["permission"] == "OWNER"), None)
        operator = group.member(str(operator_id)) if operator_id else group
        context = Context(
            account,
            operator,
            member,
            group,
            group.member(account_route["account"]),
        )
        return MetadataModified(
            context,
            member,
            Nick,
            {Nick.inh(lambda x: x.badge): ModifyDetail("update", raw_event["current"], raw_event["origin"])},
            operator=operator,
            scene=group,
        )

    @EventParse.collect(m, "MemberPermissionChangeEvent")
    async def member_permission_change(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["member"]["group"]["id"]))
        member = group.member(str(raw_event["member"]["id"]))
        members = await self.connection.call("fetch", "memberList", {"target": raw_event["group"]["id"]})
        members = cast("list[dict]", members)
        operator_id = next((d["id"] for d in members if d["permission"] == "OWNER"), None)
        operator = group.member(str(operator_id)) if operator_id else group
        context = Context(
            account,
            operator,
            member,
            group,
            group.member(account_route["account"]),
        )
        available = PRIVILEGE_LEVEL[raw_event["current"]] > PRIVILEGE_LEVEL[raw_event["origin"]]
        return MetadataModified(
            context,
            member,
            Privilege,
            {
                Privilege.inh(lambda x: x.available): ModifyDetail("update", available, not available),
                Privilege.inh(lambda x: x.effective): ModifyDetail("update", available, not available),
            },
            operator=operator,
            scene=group,
        )

    @EventParse.collect(m, "MemberMuteEvent")
    async def member_mute(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["member"]["group"]["id"]))
        operator = group.member(str(raw_event["operator"]["id"])) if raw_event.get("operator") else None
        member = group.member(str(raw_event["member"]["id"]))
        context = Context(
            account,
            operator or group.member(account_route["account"]),  # bot self if no operator
            member,
            group,
            group.member(account_route["account"]),
        )
        return MetadataModified(
            context,
            member,
            MuteInfo,
            {
                MuteInfo.inh(lambda x: x.muted): ModifyDetail("update", True, False),
                MuteInfo.inh(lambda x: x.duration): ModifyDetail(
                    "set", timedelta(seconds=raw_event["durationSeconds"]), None
                ),
            },
            operator=operator or group.member(account_route["account"]),
            scene=group,
        )

    @EventParse.collect(m, "MemberUnmuteEvent")
    async def member_unmute(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["member"]["group"]["id"]))
        operator = group.member(str(raw_event["operator"]["id"])) if raw_event.get("operator") else None
        member = group.member(str(raw_event["member"]["id"]))
        context = Context(
            account,
            operator or group.member(account_route["account"]),  # bot self if no operator
            member,
            group,
            group.member(account_route["account"]),
        )
        return MetadataModified(
            context,
            member,
            MuteInfo,
            {
                MuteInfo.inh(lambda x: x.muted): ModifyDetail("update", False, True),
                MuteInfo.inh(lambda x: x.duration): ModifyDetail("set", None, timedelta(0)),
            },
            operator=operator or group.member(account_route["account"]),
            scene=group,
        )

    @EventParse.collect(m, "MemberHonorChangeEvent")
    async def member_honor_change(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["member"]["group"]["id"]))
        member = group.member(str(raw_event["member"]["id"]))
        context = Context(
            account,
            group,
            member,
            group,
            group.member(account_route["account"]),
        )
        return MetadataModified(
            context,
            member,
            Honor,
            {
                Honor.inh(lambda x: x.name): (
                    ModifyDetail("set", raw_event["honor"], None)
                    if raw_event["action"] == "achieve"
                    else ModifyDetail("clear", None, raw_event["honor"])
                )
            },
            scene=group,
        )
