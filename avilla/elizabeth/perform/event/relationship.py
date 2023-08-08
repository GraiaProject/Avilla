from __future__ import annotations

from avilla.core.context import Context
from avilla.core.event import RelationshipCreated, RelationshipDestroyed
from avilla.core.selector import Selector
from avilla.elizabeth.collector.connection import ConnectionCollector

from . import ElizabethEventParse


class ElizabethEventRelationshipPerform((m := ConnectionCollector())._):
    m.post_applying = True

    @m.entity(ElizabethEventParse, "MemberJoinEvent")
    async def member_join(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["member"]["group"]["id"]))
        member = group.member(str(raw_event["member"]["id"]))
        inviter = group.member(str(raw_event["inviter"]["id"])) if raw_event.get("inviter") else None
        context = Context(
            account,
            member,
            group,
            group,
            group.member(account_route["account"]),
            mediums=[inviter] if inviter else None,
        )
        return RelationshipCreated(context)

    @m.entity(ElizabethEventParse, "MemberLeaveEventKick")
    async def member_leave_kick(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["member"]["group"]["id"]))
        member = group.member(str(raw_event["member"]["id"]))
        operator = group.member(str(raw_event["operator"]["id"])) if raw_event.get("operator") else None
        context = Context(
            account,
            operator or group.member(account_route["account"]),  # bot self if no operator
            member,
            group,
            group.member(account_route["account"]),
        )
        return RelationshipDestroyed(context, active=False)

    @m.entity(ElizabethEventParse, "MemberLeaveEventQuit")
    async def member_leave_quit(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["member"]["group"]["id"]))
        member = group.member(str(raw_event["member"]["id"]))
        context = Context(
            account,
            member,
            member,
            group,
            group.member(account_route["account"]),
        )
        return RelationshipDestroyed(context, active=True)

    @m.entity(ElizabethEventParse, "BotJoinGroupEvent")
    async def bot_join_group(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["group"]["id"]))
        inviter = group.member(str(raw_event["inviter"]["id"])) if raw_event.get("inviter") else None
        context = Context(
            account,
            group.member(account_route["account"]),
            group,
            group,
            group.member(account_route["account"]),
            mediums=[inviter] if inviter else None,
        )
        return RelationshipCreated(context)

    @m.entity(ElizabethEventParse, "BotLeaveEventActive")
    async def bot_leave_active(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["group"]["id"]))
        context = Context(
            account,
            group.member(account_route["account"]),
            group.member(account_route["account"]),
            group,
            group.member(account_route["account"]),
        )
        return RelationshipDestroyed(context, active=True)

    @m.entity(ElizabethEventParse, "BotLeaveEventKick")
    async def bot_leave_kick(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["group"]["id"]))
        operator = group.member(str(raw_event["operator"]["id"]))
        context = Context(
            account,
            operator,
            group.member(account_route["account"]),
            group,
            group.member(account_route["account"]),
        )
        return RelationshipDestroyed(context, active=False)

    @m.entity(ElizabethEventParse, "BotLeaveEventDisband")
    async def bot_leave_disband(self, raw_event: dict):
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
        return RelationshipDestroyed(context, active=False, indirect=True)
