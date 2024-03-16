from __future__ import annotations

from datetime import timedelta
from typing import cast

from avilla.core.context import Context
from avilla.core.event import MetadataModified, ModifyDetail
from avilla.core.selector import Selector
from avilla.elizabeth.capability import ElizabethCapability
from avilla.elizabeth.collector.connection import ConnectionCollector
from avilla.elizabeth.const import PRIVILEGE_LEVEL
from avilla.standard.core.privilege import MuteInfo, Privilege
from avilla.standard.core.profile import Nick, Summary
from avilla.standard.qq.honor import Honor


class ElizabethEventGroupMemberPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/elizabeth::event"
    m.identify = "member"

    @m.entity(ElizabethCapability.event_callback, raw_event="MemberCardChangeEvent")
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
            Nick(group_data["name"], group_data["name"], None),
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
            {Nick.inh().nickname: ModifyDetail("update", raw_event["current"], raw_event["origin"])},
            operator=operator or group.member(account_route["account"]),
            scene=group,
        )

    @m.entity(ElizabethCapability.event_callback, raw_event="MemberSpecialTitleChangeEvent")
    async def member_special_title_change(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        member_data = raw_event["member"]
        group_data = member_data["group"]
        group = land.group(str(group_data["id"]))
        member = group.member(str(member_data["id"]))
        members = await self.connection.call("fetch", "memberList", {"target": member_data["group"]["id"]})
        members = cast(list[dict], members)
        operator_data = next((d for d in members if d["permission"] == "OWNER"), None)
        operator = group.member(str(operator_data["id"])) if operator_data else group.member(account_route["account"])
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
            Nick(group_data["name"], group_data["name"], None),
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
            {Nick.inh().badge: ModifyDetail("update", raw_event["current"], raw_event["origin"])},
            operator=operator,
            scene=group,
        )

    @m.entity(ElizabethCapability.event_callback, raw_event="MemberPermissionChangeEvent")
    async def member_permission_change(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        member_data = raw_event["member"]
        group_data = member_data["group"]
        group = land.group(str(group_data["id"]))
        member = group.member(str(member_data["id"]))
        members = await self.connection.call("fetch", "memberList", {"target": group_data["id"]})
        members = cast(list[dict], members)
        operator_data = next((d for d in members if d["permission"] == "OWNER"), None)
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
            Nick(group_data["name"], group_data["name"], None),
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
                Privilege.inh().available: ModifyDetail("update", available, not available),
                Privilege.inh().effective: ModifyDetail("update", available, not available),
            },
            operator=operator,
            scene=group,
        )

    @m.entity(ElizabethCapability.event_callback, raw_event="MemberMuteEvent")
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
            Nick(group_data["name"], group_data["name"], None),
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
                MuteInfo.inh().muted: ModifyDetail("update", True, False),
                MuteInfo.inh().duration: ModifyDetail("set", timedelta(seconds=raw_event["durationSeconds"]), None),
            },
            operator=operator or group.member(account_route["account"]),
            scene=group,
        )

    @m.entity(ElizabethCapability.event_callback, raw_event="MemberUnmuteEvent")
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
            Nick(group_data["name"], group_data["name"], None),
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
                MuteInfo.inh().muted: ModifyDetail("update", False, True),
                MuteInfo.inh().duration: ModifyDetail("set", timedelta(seconds=0)),
            },
            operator=operator or group.member(account_route["account"]),
            scene=group,
        )

    @m.entity(ElizabethCapability.event_callback, raw_event="MemberHonorChangeEvent")
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
            Nick(group_data["name"], group_data["name"], None),
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
                Honor.inh().name: (
                    ModifyDetail("set", raw_event["honor"], None)
                    if raw_event["action"] == "achieve"
                    else ModifyDetail("clear", None, raw_event["honor"])
                )
            },
            scene=group,
        )
