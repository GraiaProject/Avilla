from __future__ import annotations

from datetime import datetime

from flywheel import scoped_collect

from avilla.core.context import Context
from avilla.core.request import Request
from avilla.core.selector import Selector
from avilla.satori.bases import InstanceOfAccount
from avilla.satori.capability import SatoriCapability
from avilla.satori.const import land as LAND
from satori.event import GuildMemberEvent, UserEvent, GuildEvent
from avilla.standard.core.profile.metadata import Nick, Summary
from avilla.standard.core.request import RequestReceived


class SatoriEventRequestPerform(m := scoped_collect.globals().target, InstanceOfAccount, static=True):

    @m.impl(SatoriCapability.event_callback, raw_event="guild-member-request")
    async def member_join_request(self, event: GuildMemberEvent):
        account = self.account
        land = Selector().land(account.route["land"])
        guild = land.guild(event.guild.id)
        sender = land.user(event.user.id)
        context = Context(
            account,
            sender,
            guild,
            guild,
            guild.member(account.route["account"]),
            mediums=[guild.member(event.operator.id)] if event.operator else None,
        )
        request = Request(
            f"{event.message.id if event.message else event.id}",
            LAND(account.route["land"]),
            guild,
            sender,
            account,
            datetime.now(),
            request_type="satori::guild-member-request",
            message=event.message.content if event.message else None,
        )
        context._collect_metadatas(
            guild,
            Nick(event.guild.name, event.guild.name, None),  # type: ignore
            Summary(event.guild.name, None),  # type: ignore
        )
        context._collect_metadatas(
            sender,
            Nick(event.user.name, event.member.nick or event.user.name, None),  # type: ignore
            Summary(event.user.name, None),  # type: ignore
        )
        return RequestReceived(context, request)

    @m.impl(SatoriCapability.event_callback, raw_event="friend-request")
    async def new_friend_request(self, event: UserEvent):
        account = self.account
        land = Selector().land(account.route["land"])
        sender = land.user(event.user.id)
        context = Context(
            account,
            sender,
            account.route,
            sender,
            account.route,
        )
        request = Request(
            f"{event.message.id if event.message else event.id}",
            LAND(account.route["land"]),
            sender,
            sender,
            account,
            datetime.now(),
            request_type="satori::friend-request",
            message=event.message.content if event.message else None,
        )
        context._collect_metadatas(
            sender,
            Nick(event.user.name, event.user.name, None),  # type: ignore
            Summary(event.user.name, None),  # type: ignore
        )
        return RequestReceived(context, request)

    @m.impl(SatoriCapability.event_callback, raw_event="guild-request")
    async def bot_invited_join_group_request(self, event: GuildEvent):
        account = self.account
        land = Selector().land(account.route["land"])
        guild = land.guild(event.guild.id)
        operator = guild.member(event.operator.id) if event.operator else guild
        context = Context(
            account,
            operator,
            account.route,
            operator,
            account.route,
        )
        request = Request(
            f"{event.message.id if event.message else event.id}",
            LAND(account.route["land"]),
            operator,
            operator,
            account,
            datetime.now(),
            request_type="satori::guild-request",
            message=event.message.content if event.message else None,
        )
        context._collect_metadatas(
            guild,
            Nick(event.guild.name, event.guild.name, None),  # type: ignore
            Summary(event.guild.name, None),  # type: ignore
        )
        if event.operator:
            context._collect_metadatas(
                operator,
                Nick(event.operator.name, event.operator.name, None),  # type: ignore
                Summary(event.operator.name, None),  # type: ignore
            )
        return RequestReceived(context, request)
