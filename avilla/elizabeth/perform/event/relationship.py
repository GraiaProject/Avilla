from __future__ import annotations

from datetime import timedelta

from avilla.core.context import Context
from avilla.core.event import (
    MemberCreated,
    MemberDestroyed,
    SceneCreated,
    SceneDestroyed,
    DirectSessionCreated,
    DirectSessionDestroyed
)
from avilla.core.selector import Selector
from avilla.elizabeth.capability import ElizabethCapability
from avilla.elizabeth.collector.connection import ConnectionCollector
from avilla.elizabeth.const import PRIVILEGE_LEVEL
from avilla.standard.core.privilege import MuteInfo, Privilege
from avilla.standard.core.profile import Nick, Summary


class ElizabethEventRelationshipPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/elizabeth::event"
    m.identify = "relationship"

    @m.entity(ElizabethCapability.event_callback, raw_event="FriendAddEvent")
    async def friend_add(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        friend_data = raw_event["friend"]
        friend = land.friend(str(friend_data["id"]))
        context = Context(
            account,
            friend,
            account_route,
            friend,
            account_route,
        )
        context._collect_metadatas(
            friend,
            Nick(friend_data["nickname"], friend_data["nickname"], friend_data.get("remark")),
            Summary(friend_data["nickname"], None),
        )
        return DirectSessionCreated(context)

    @m.entity(ElizabethCapability.event_callback, raw_event="FriendDeleteEvent")
    async def friend_delete(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        friend_data = raw_event["friend"]
        friend = land.friend(str(friend_data["id"]))
        context = Context(
            account,
            friend,
            account_route,
            friend,
            account_route,
        )
        context._collect_metadatas(
            friend,
            Nick(friend_data["nickname"], friend_data["nickname"], friend_data.get("remark")),
            Summary(friend_data["nickname"], None),
        )
        return DirectSessionDestroyed(context, active=True)

    @m.entity(ElizabethCapability.event_callback, raw_event="MemberJoinEvent")
    async def member_join(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        member_data = raw_event["member"]
        group_data = member_data["group"]
        group = land.group(str(group_data["id"]))
        member = group.member(str(member_data["id"]))
        inviter = group.member(str(raw_event["inviter"]["id"])) if raw_event.get("inviter") else None
        context = Context(
            account,
            member,
            group,
            group,
            group.member(account_route["account"]),
            mediums=[inviter] if inviter else None,
        )
        if inviter_data := raw_event.get("inviter"):
            context._collect_metadatas(
                group.member(str(inviter_data["id"])),
                Nick(inviter_data["memberName"], inviter_data["memberName"], inviter_data.get("specialTitle")),
                Summary(inviter_data["memberName"], "a group member assigned to this account"),
                MuteInfo(
                    inviter_data.get("mutetimeRemaining") is not None,
                    timedelta(seconds=inviter_data.get("mutetimeRemaining", 0)),
                    None,
                ),
                Privilege(
                    PRIVILEGE_LEVEL[inviter_data["permission"]] > 0,
                    PRIVILEGE_LEVEL[group_data["permission"]] > PRIVILEGE_LEVEL[inviter_data["permission"]],
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
        return MemberCreated(context)

    @m.entity(ElizabethCapability.event_callback, raw_event="MemberLeaveEventKick")
    async def member_leave_kick(self, raw_event: dict):
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
        return MemberDestroyed(context, active=False)

    @m.entity(ElizabethCapability.event_callback, raw_event="MemberLeaveEventQuit")
    async def member_leave_quit(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        member_data = raw_event["member"]
        group_data = member_data["group"]
        group = land.group(str(group_data["id"]))
        member = group.member(str(member_data["id"]))
        context = Context(
            account,
            member,
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
        return MemberDestroyed(context, active=True)

    @m.entity(ElizabethCapability.event_callback, raw_event="BotJoinGroupEvent")
    async def bot_join_group(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group_data = raw_event["group"]
        group = land.group(str(group_data["id"]))
        inviter = group.member(str(raw_event["inviter"]["id"])) if raw_event.get("inviter") else None
        context = Context(
            account,
            group.member(account_route["account"]),
            group,
            group,
            group.member(account_route["account"]),
            mediums=[inviter] if inviter else None,
        )
        if inviter_data := raw_event.get("inviter"):
            context._collect_metadatas(
                group.member(str(inviter_data["id"])),
                Nick(inviter_data["memberName"], inviter_data["memberName"], inviter_data.get("specialTitle")),
                Summary(inviter_data["memberName"], "a group member assigned to this account"),
                MuteInfo(
                    inviter_data.get("mutetimeRemaining") is not None,
                    timedelta(seconds=inviter_data.get("mutetimeRemaining", 0)),
                    None,
                ),
                Privilege(
                    PRIVILEGE_LEVEL[inviter_data["permission"]] > 0,
                    PRIVILEGE_LEVEL[group_data["permission"]] > PRIVILEGE_LEVEL[inviter_data["permission"]],
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
        return SceneCreated(context)

    @m.entity(ElizabethCapability.event_callback, raw_event="BotLeaveEventActive")
    async def bot_leave_active(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group_data = raw_event["group"]
        group = land.group(str(raw_event["group"]["id"]))
        context = Context(
            account,
            group.member(account_route["account"]),
            group,
            group,
            group.member(account_route["account"]),
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
        return SceneDestroyed(context, active=True)

    @m.entity(ElizabethCapability.event_callback, raw_event="BotLeaveEventKick")
    async def bot_leave_kick(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group_data = raw_event["group"]
        operator_data = raw_event["operator"]
        group = land.group(str(raw_event["group"]["id"]))
        operator = group.member(str(raw_event["operator"]["id"]))
        context = Context(
            account,
            operator,
            group,
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
        return SceneDestroyed(context, active=False)

    @m.entity(ElizabethCapability.event_callback, raw_event="BotLeaveEventDisband")
    async def bot_leave_disband(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group_data = raw_event["group"]
        group = land.group(str(raw_event["group"]["id"]))
        operator = group.member(str(raw_event["operator"]["id"])) if raw_event.get("operator") else None
        context = Context(
            account,
            operator or group.member(account_route["account"]),  # bot self if no operator
            group,
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
            group,
            Nick(group_data["name"], group_data["name"], None),
            Summary(group_data["name"], None),
            Privilege(
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
            ),
        )
        return SceneDestroyed(context, active=False, indirect=True)
