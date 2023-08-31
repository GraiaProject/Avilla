from __future__ import annotations

from datetime import timedelta
from typing import cast

from avilla.core.context import Context
from avilla.core.event import MetadataModified, ModifyDetail
from avilla.core.selector import Selector
from avilla.elizabeth.collector.connection import ConnectionCollector
from avilla.elizabeth.const import PRIVILEGE_LEVEL
from avilla.standard.core.privilege import MuteInfo, Privilege
from avilla.standard.core.profile import Nick, Summary
from avilla.standard.qq.honor import Honor

from . import ElizabethEventParse


class ElizabethEventGroupMemberPerform((m := ConnectionCollector())._):
    m.post_applying = True

    @m.entity(ElizabethEventParse, "MemberCardChangeEvent")
    async def member_card_change(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        member_data = raw_event["member"]
        group_data = member_data["group"]
        group = land.group(str(group_data["id"]))
        member = group.member(str(member_data["id"]))
        operator = group.member(str(raw_event["operator"]["id"])) if raw_event.get("operator") else None
        context = Context(
            account,
            operator or group.member(account_route["account"]),
            member,
            group,
            group.member(account_route["account"]),
        )
        if operator_data := raw_event.get("operator"):
            context._collect_metadatas(
                group.member(str(operator_data["id"])),
                Nick(operator_data["memberName"], operator_data["memberName"], operator_data.get("specialTitle")),
                Summary(operator_data["memberName"], "a group member assigned to this account"),
                MuteInfo(
                    operator_data.get("mutetimeRemaining") is not None,
                    timedelta(seconds=operator_data.get("mutetimeRemaining", 0)),
                    None,
                ),
                Privilege(
                    PRIVILEGE_LEVEL[operator_data["permission"]] > 0,
                    PRIVILEGE_LEVEL[group_data["permission"]] > PRIVILEGE_LEVEL[operator_data["permission"]],
                ),
            )
        context._collect_metadatas(
            member,
            Nick(member_data["memberName"], member_data["memberName"], member_data.get("specialTitle")),
            Summary(member_data["memberName"], "a group member assigned to this account"),
            MuteInfo(
                member_data.get("mutetimeRemaining") is not None,
                timedelta(seconds=member_data.get("mutetimeRemaining", 0)),
                None,
            ),
            Privilege(
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
            ),
        )
        context._collect_metadatas(
            group,
            Summary(group_data["name"], None),
            Privilege(
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
            ),
        )
        return MetadataModified(
            context,
            member,
            Nick,
            {Nick.inh(lambda x: x.nickname): ModifyDetail("update", raw_event["current"], raw_event["origin"])},
            operator=operator or group.member(account_route["account"]),
            scene=group,
        )

    @m.entity(ElizabethEventParse, "MemberSpecialTitleChangeEvent")
    async def member_special_title_change(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        member_data = raw_event["member"]
        group_data = member_data["group"]
        group = land.group(str(group_data["id"]))
        member = group.member(str(member_data["id"]))
        members = await self.connection.call("fetch", "memberList", {"target": raw_event["group"]["id"]})
        members = cast(list[dict], members)
        operator_data = next((d for d in members if d["id"] == raw_event["operator"]["id"]), None)
        operator = group.member(str(operator_data["id"])) if operator_data else group
        context = Context(
            account,
            operator,
            member,
            group,
            group.member(account_route["account"]),
        )
        if operator_data:
            context._collect_metadatas(
                operator,
                Nick(operator_data["memberName"], operator_data["memberName"], operator_data.get("specialTitle")),
                Summary(operator_data["memberName"], "a group member assigned to this account"),
                MuteInfo(
                    operator_data.get("mutetimeRemaining") is not None,
                    timedelta(seconds=operator_data.get("mutetimeRemaining", 0)),
                    None,
                ),
                Privilege(
                    PRIVILEGE_LEVEL[operator_data["permission"]] > 0,
                    PRIVILEGE_LEVEL[group_data["permission"]] > PRIVILEGE_LEVEL[operator_data["permission"]],
                ),
            )
        context._collect_metadatas(
            member,
            Nick(member_data["memberName"], member_data["memberName"], member_data.get("specialTitle")),
            Summary(member_data["memberName"], "a group member assigned to this account"),
            MuteInfo(
                member_data.get("mutetimeRemaining") is not None,
                timedelta(seconds=member_data.get("mutetimeRemaining", 0)),
                None,
            ),
            Privilege(
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
            ),
        )
        context._collect_metadatas(
            group,
            Summary(group_data["name"], None),
            Privilege(
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
            ),
        )
        return MetadataModified(
            context,
            member,
            Nick,
            {Nick.inh(lambda x: x.badge): ModifyDetail("update", raw_event["current"], raw_event["origin"])},
            operator=operator,
            scene=group,
        )

    @m.entity(ElizabethEventParse, "MemberPermissionChangeEvent")
    async def member_permission_change(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        member_data = raw_event["member"]
        group_data = member_data["group"]
        group = land.group(str(group_data["id"]))
        member = group.member(str(member_data["id"]))
        members = await self.connection.call("fetch", "memberList", {"target": raw_event["group"]["id"]})
        members = cast(list[dict], members)
        operator_data = next((d for d in members if d["id"] == raw_event["operator"]["id"]), None)
        operator = group.member(str(operator_data["id"])) if operator_data else group
        context = Context(
            account,
            operator,
            member,
            group,
            group.member(account_route["account"]),
        )
        if operator_data:
            context._collect_metadatas(
                operator,
                Nick(operator_data["memberName"], operator_data["memberName"], operator_data.get("specialTitle")),
                Summary(operator_data["memberName"], "a group member assigned to this account"),
                MuteInfo(
                    operator_data.get("mutetimeRemaining") is not None,
                    timedelta(seconds=operator_data.get("mutetimeRemaining", 0)),
                    None,
                ),
                Privilege(
                    PRIVILEGE_LEVEL[operator_data["permission"]] > 0,
                    PRIVILEGE_LEVEL[group_data["permission"]] > PRIVILEGE_LEVEL[operator_data["permission"]],
                ),
            )
        context._collect_metadatas(
            member,
            Nick(member_data["memberName"], member_data["memberName"], member_data.get("specialTitle")),
            Summary(member_data["memberName"], "a group member assigned to this account"),
            MuteInfo(
                member_data.get("mutetimeRemaining") is not None,
                timedelta(seconds=member_data.get("mutetimeRemaining", 0)),
                None,
            ),
            Privilege(
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
            ),
        )
        context._collect_metadatas(
            group,
            Summary(group_data["name"], None),
            Privilege(
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
            ),
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

    @m.entity(ElizabethEventParse, "MemberMuteEvent")
    async def member_mute(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        member_data = raw_event["member"]
        group_data = member_data["group"]
        group = land.group(str(group_data["id"]))
        member = group.member(str(member_data["id"]))
        operator = group.member(str(raw_event["operator"]["id"])) if raw_event.get("operator") else None
        context = Context(
            account,
            operator or group.member(account_route["account"]),  # bot self if no operator
            member,
            group,
            group.member(account_route["account"]),
        )
        if operator_data := raw_event.get("operator"):
            context._collect_metadatas(
                group.member(str(operator_data["id"])),
                Nick(operator_data["memberName"], operator_data["memberName"], operator_data.get("specialTitle")),
                Summary(operator_data["memberName"], "a group member assigned to this account"),
                MuteInfo(
                    operator_data.get("mutetimeRemaining") is not None,
                    timedelta(seconds=operator_data.get("mutetimeRemaining", 0)),
                    None,
                ),
                Privilege(
                    PRIVILEGE_LEVEL[operator_data["permission"]] > 0,
                    PRIVILEGE_LEVEL[group_data["permission"]] > PRIVILEGE_LEVEL[operator_data["permission"]],
                ),
            )
        context._collect_metadatas(
            member,
            Nick(member_data["memberName"], member_data["memberName"], member_data.get("specialTitle")),
            Summary(member_data["memberName"], "a group member assigned to this account"),
            MuteInfo(
                member_data.get("mutetimeRemaining") is not None,
                timedelta(seconds=member_data.get("mutetimeRemaining", 0)),
                None,
            ),
            Privilege(
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
            ),
        )
        context._collect_metadatas(
            group,
            Summary(group_data["name"], None),
            Privilege(
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
            ),
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

    @m.entity(ElizabethEventParse, "MemberUnmuteEvent")
    async def member_unmute(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        member_data = raw_event["member"]
        group_data = member_data["group"]
        group = land.group(str(group_data["id"]))
        member = group.member(str(member_data["id"]))
        operator = group.member(str(raw_event["operator"]["id"])) if raw_event.get("operator") else None
        context = Context(
            account,
            operator or group.member(account_route["account"]),  # bot self if no operator
            member,
            group,
            group.member(account_route["account"]),
        )
        if operator_data := raw_event.get("operator"):
            context._collect_metadatas(
                group.member(str(operator_data["id"])),
                Nick(operator_data["memberName"], operator_data["memberName"], operator_data.get("specialTitle")),
                Summary(operator_data["memberName"], "a group member assigned to this account"),
                MuteInfo(
                    operator_data.get("mutetimeRemaining") is not None,
                    timedelta(seconds=operator_data.get("mutetimeRemaining", 0)),
                    None,
                ),
                Privilege(
                    PRIVILEGE_LEVEL[operator_data["permission"]] > 0,
                    PRIVILEGE_LEVEL[group_data["permission"]] > PRIVILEGE_LEVEL[operator_data["permission"]],
                ),
            )
        context._collect_metadatas(
            member,
            Nick(member_data["memberName"], member_data["memberName"], member_data.get("specialTitle")),
            Summary(member_data["memberName"], "a group member assigned to this account"),
            MuteInfo(
                member_data.get("mutetimeRemaining") is not None,
                timedelta(seconds=member_data.get("mutetimeRemaining", 0)),
                None,
            ),
            Privilege(
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
            ),
        )
        context._collect_metadatas(
            group,
            Summary(group_data["name"], None),
            Privilege(
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
            ),
        )
        return MetadataModified(
            context,
            member,
            MuteInfo,
            {
                MuteInfo.inh(lambda x: x.muted): ModifyDetail("update", False, True),
                MuteInfo.inh(lambda x: x.duration): ModifyDetail("set", timedelta(seconds=0)),
            },
            operator=operator or group.member(account_route["account"]),
            scene=group,
        )

    @m.entity(ElizabethEventParse, "MemberHonorChangeEvent")
    async def member_honor_change(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        member_data = raw_event["member"]
        group_data = member_data["group"]
        group = land.group(str(group_data["id"]))
        member = group.member(str(member_data["id"]))
        context = Context(
            account,
            group,
            member,
            group,
            group.member(account_route["account"]),
        )
        context._collect_metadatas(
            member,
            Nick(member_data["memberName"], member_data["memberName"], member_data.get("specialTitle")),
            Summary(member_data["memberName"], "a group member assigned to this account"),
            MuteInfo(
                member_data.get("mutetimeRemaining") is not None,
                timedelta(seconds=member_data.get("mutetimeRemaining", 0)),
                None,
            ),
            Privilege(
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
            ),
        )
        context._collect_metadatas(
            group,
            Summary(group_data["name"], None),
            Privilege(
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
            ),
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
