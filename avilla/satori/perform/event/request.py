from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from avilla.core.context import Context
from avilla.core.request import Request
from avilla.core.selector import Selector
from avilla.satori.const import land as LAND
from avilla.satori.capability import SatoriCapability
from avilla.satori.collector.connection import ConnectionCollector
from satori.event import GuildMemberEvent, UserEvent, GuildEvent

from avilla.standard.core.profile.metadata import Nick, Summary
from avilla.standard.core.request import RequestReceived
from satori.model import Event

class SatoriEventRequestPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/satori::event"
    m.identify = "request"

    @m.entity(SatoriCapability.event_callback, raw_event="guild-member-request")
    async def member_join_request(self, raw_event: Event):
        account = self.protocol.service._accounts[self.connection.identity]
        land = Selector().land(account.route["land"])
        if TYPE_CHECKING:
            assert isinstance(raw_event, GuildMemberEvent)
        guild = land.guild(raw_event.guild.id)
        sender = land.user(raw_event.user.id)
        context = Context(
            account,
            sender,
            guild,
            guild,
            guild.member(account.route["account"]),
            mediums=[guild.member(raw_event.operator.id)] if raw_event.operator else None,
        )
        request = Request(
            f"{raw_event.message.id if raw_event.message else raw_event.id}",
            LAND(account.route["land"]),
            guild,
            sender,
            account,
            datetime.now(),
            request_type="satori::guild-member-request",
            message=raw_event.message.content if raw_event.message else None,
        )
        context._collect_metadatas(
            guild,
            Nick(raw_event.guild.name, raw_event.guild.name, None),  # type: ignore
            Summary(raw_event.guild.name, None),  # type: ignore
        )
        context._collect_metadatas(
            sender,
            Nick(raw_event.user.name, raw_event.member.nick or raw_event.user.name, None),  # type: ignore
            Summary(raw_event.user.name, None),  # type: ignore
        )
        return RequestReceived(context, request)

    @m.entity(SatoriCapability.event_callback, raw_event="friend-request")
    async def new_friend_request(self, raw_event: Event):
        account = self.protocol.service._accounts[self.connection.identity]
        land = Selector().land(account.route["land"])
        if TYPE_CHECKING:
            assert isinstance(raw_event, UserEvent)
        sender = land.user(raw_event.user.id)
        context = Context(
            account,
            sender,
            account.route,
            sender,
            account.route,
        )
        request = Request(
            f"{raw_event.message.id if raw_event.message else raw_event.id}",
            LAND(account.route["land"]),
            sender,
            sender,
            account,
            datetime.now(),
            request_type="satori::friend-request",
            message=raw_event.message.content if raw_event.message else None,
        )
        context._collect_metadatas(
            sender,
            Nick(raw_event.user.name, raw_event.user.name, None),  # type: ignore
            Summary(raw_event.user.name, None),  # type: ignore
        )
        return RequestReceived(context, request)

    @m.entity(SatoriCapability.event_callback, raw_event="guild-request")
    async def bot_invited_join_group_request(self, raw_event: Event):
        account = self.protocol.service._accounts[self.connection.identity]
        land = Selector().land(account.route["land"])
        if TYPE_CHECKING:
            assert isinstance(raw_event, GuildEvent)
        guild = land.guild(raw_event.guild.id)
        operator = guild.member(raw_event.operator.id) if raw_event.operator else guild
        context = Context(
            account,
            operator,
            account.route,
            operator,
            account.route,
        )
        request = Request(
            f"{raw_event.message.id if raw_event.message else raw_event.id}",
            LAND(account.route["land"]),
            operator,
            operator,
            account,
            datetime.now(),
            request_type="satori::guild-request",
            message=raw_event.message.content if raw_event.message else None,
        )
        context._collect_metadatas(
            guild,
            Nick(raw_event.guild.name, raw_event.guild.name, None),  # type: ignore
            Summary(raw_event.guild.name, None),  # type: ignore
        )
        if raw_event.operator:
            context._collect_metadatas(
                operator,
                Nick(raw_event.operator.name, raw_event.operator.name, None),  # type: ignore
                Summary(raw_event.operator.name, None),  # type: ignore
            )
        return RequestReceived(context, request)
