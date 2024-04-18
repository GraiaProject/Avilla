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
from avilla.standard.qq.announcement import Announcement


class ElizabethEventGroupPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/elizabeth::event"
    m.identify = "group"

    @m.entity(ElizabethCapability.event_callback, raw_event="BotGroupPermissionChangeEvent")
    async def bot_group_permission_change(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["group"]["id"]))
        members = await self.connection.call("fetch", "memberList", {"target": raw_event["group"]["id"]})
        members = cast(list[dict], members)
        operator_data = next((d for d in members if d["permission"] == "OWNER"), None)
        operator = group.member(str(operator_data["id"])) if operator_data else group
        context = Context(
            account,
            operator,
            group.member(account_route["account"]),
            group,
            group.member(account_route["account"]),
        )
        group_data = raw_event["group"]
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
                Privilege(True, False),
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
            group.member(account_route["account"]),
            Privilege,
            {
                Privilege.inh().available: ModifyDetail("update", available, not available),
                Privilege.inh().effective: ModifyDetail("update", available, not available),
            },
            operator=operator,
            scene=group,
        )

    @m.entity(ElizabethCapability.event_callback, raw_event="BotMuteEvent")
    async def bot_mute(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        operator_data = raw_event["operator"]
        group_data = raw_event["group"]
        group = land.group(str(group_data["id"]))
        operator = group.member(str(operator_data["id"]))
        context = Context(
            account,
            operator,
            group.member(account_route["account"]),
            group,
            group.member(account_route["account"]),
        )
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
            group.member(account_route["account"]),
            MuteInfo,
            {
                MuteInfo.inh().muted: ModifyDetail("update", True, False),
                MuteInfo.inh().duration: ModifyDetail("set", timedelta(seconds=raw_event["durationSeconds"]), None),
            },
            operator=operator,
            scene=group,
        )

    @m.entity(ElizabethCapability.event_callback, raw_event="BotUnmuteEvent")
    async def bot_unmute(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        operator_data = raw_event["operator"]
        group_data = raw_event["group"]
        group = land.group(str(group_data["id"]))
        operator = group.member(str(operator_data["id"]))
        context = Context(
            account,
            operator,
            group.member(account_route["account"]),
            group,
            group.member(account_route["account"]),
        )
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
            group.member(account_route["account"]),
            MuteInfo,
            {
                MuteInfo.inh().muted: ModifyDetail("update", False, True),
                MuteInfo.inh().duration: ModifyDetail("clear", timedelta(seconds=0)),
            },
            operator=operator,
            scene=group,
        )

    @m.entity(ElizabethCapability.event_callback, raw_event="GroupNameChangeEvent")
    async def group_name_change(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["group"]["id"]))
        operator = group.member(str(raw_event["operator"]["id"])) if raw_event.get("operator") else None
        context = Context(
            account,
            operator or group.member(account_route["account"]),  # bot self if no operator
            group,
            group,
            group.member(account_route["account"]),
        )
        group_data = raw_event["group"]
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
            group,
            Summary,
            {Summary.inh().name: ModifyDetail("update", raw_event["current"], raw_event["origin"])},
            operator=operator or group.member(account_route["account"]),
            scene=group,
        )

    @m.entity(ElizabethCapability.event_callback, raw_event="GroupMuteAllEvent")
    async def group_mute_all(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["group"]["id"]))
        operator = group.member(str(raw_event["operator"]["id"])) if raw_event.get("operator") else None
        context = Context(
            account,
            operator or group.member(account_route["account"]),  # bot self if no operator
            group,
            group,
            group.member(account_route["account"]),
        )
        group_data = raw_event["group"]
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
            group,
            MuteInfo,
            {
                MuteInfo.inh().muted: ModifyDetail("update", raw_event["current"], raw_event["origin"]),
            },
            operator=operator or group.member(account_route["account"]),  # bot self if no operator
            scene=group,
        )

    @m.entity(ElizabethCapability.event_callback, raw_event="GroupEntranceAnnouncementChangeEvent")
    async def group_entrance_announcement_change(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["group"]["id"]))
        operator = group.member(str(raw_event["operator"]["id"])) if raw_event.get("operator") else None
        context = Context(
            account,
            operator or group.member(account_route["account"]),  # bot self if no operator
            group,
            group,
            group.member(account_route["account"]),
        )
        group_data = raw_event["group"]
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
            group,
            Announcement,
            {
                Announcement.inh().content: ModifyDetail("update", raw_event["current"], raw_event["origin"]),
            },
            operator=operator or group.member(account_route["account"]),  # bot self if no operator
            scene=group,
        )

    # TODO: GroupAllowAnonymousChatEvent
    # TODO: GroupAllowConfessTalkEvent
    # TODO: GroupAllowMemberInviteEvent
