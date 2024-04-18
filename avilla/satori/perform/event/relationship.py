from __future__ import annotations

from typing import TYPE_CHECKING
from avilla.core.context import Context
from avilla.core.event import (
    MemberCreated,
    MemberDestroyed,
    SceneCreated,
    SceneDestroyed,
)
from avilla.core.selector import Selector
from avilla.satori.capability import SatoriCapability
from avilla.satori.collector.connection import ConnectionCollector
from satori.event import GuildEvent, GuildMemberEvent, GuildRoleEvent
from avilla.satori.event import RoleCreated, RoleDestroyed
from satori.model import Event


class SatoriEventRelationshipPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/satori::event"
    m.identify = "relationship"

    @m.entity(SatoriCapability.event_callback, raw_event="guild-added")
    async def guild_added(self, raw_event: Event):
        account = self.protocol.service._accounts[self.connection.identity]
        land = Selector().land(account.route["land"])
        if TYPE_CHECKING:
            assert isinstance(raw_event, GuildEvent)
        guild = land.guild(raw_event.guild.id)
        inviter = guild.member(raw_event.operator.id) if raw_event.operator else guild
        context = Context(
            account,
            inviter,
            guild,
            guild,
            guild.member(account.route["account"]),
        )
        return SceneCreated(context)

    @m.entity(SatoriCapability.event_callback, raw_event="guild-removed")
    async def guild_removed(self, raw_event: Event):
        account = self.protocol.service._accounts[self.connection.identity]
        land = Selector().land(account.route["land"])
        if TYPE_CHECKING:
            assert isinstance(raw_event, GuildEvent)
        guild: Selector = land.guild(raw_event.guild.id)
        operator = guild.member(raw_event.operator.id) if raw_event.operator else guild
        context = Context(
            account,
            operator,
            guild,
            guild,
            guild.member(account.route["account"]),
        )
        return SceneDestroyed(
            context, 
            active=bool(raw_event.operator) and raw_event.operator.id == account.route["account"],
            indirect=not bool(raw_event.operator),
        )
    

    @m.entity(SatoriCapability.event_callback, raw_event="guild-member-added")
    async def guild_member_added(self, raw_event: Event):
        account = self.protocol.service._accounts[self.connection.identity]
        land = Selector().land(account.route["land"])
        if TYPE_CHECKING:
            assert isinstance(raw_event, GuildMemberEvent)
        guild = land.guild(raw_event.guild.id)
        member = guild.member(raw_event.member.user.id if raw_event.member.user else raw_event.user.id)
        operator = guild.member(raw_event.operator.id) if raw_event.operator else member
        context = Context(
            account,
            operator,
            member,
            guild,
            guild.member(account.route["account"]),
        )
        return MemberCreated(context)

    @m.entity(SatoriCapability.event_callback, raw_event="guild-member-removed")
    async def guild_member_removed(self, raw_event: Event):
        account = self.protocol.service._accounts[self.connection.identity]
        land = Selector().land(account.route["land"])
        if TYPE_CHECKING:
            assert isinstance(raw_event, GuildMemberEvent)
        guild = land.guild(raw_event.guild.id)
        member = guild.member(raw_event.member.user.id if raw_event.member.user else raw_event.user.id)
        operator = guild.member(raw_event.operator.id) if raw_event.operator else member
        context = Context(
            account,
            operator,
            member,
            guild,
            guild.member(account.route["account"]),
        )
        return MemberDestroyed(
            context, 
            active=bool(raw_event.operator) and raw_event.operator.id == member["member"],
            indirect=not bool(raw_event.operator),
        )

    @m.entity(SatoriCapability.event_callback, raw_event="guild-role-created")
    async def guild_role_created(self, raw_event: Event):
        account = self.protocol.service._accounts[self.connection.identity]
        land = Selector().land(account.route["land"])
        if TYPE_CHECKING:
            assert isinstance(raw_event, GuildRoleEvent)
        guild = land.guild(raw_event.guild.id)
        role = guild.role(raw_event.role.id)
        operator = guild.member(raw_event.operator.id) if raw_event.operator else guild
        context = Context(
            account,
            operator,
            role,
            guild,
            guild.member(account.route["account"]),
        )
        return RoleCreated(context)

    @m.entity(SatoriCapability.event_callback, raw_event="guild-role-deleted")
    async def guild_role_deleted(self, raw_event: Event):
        account = self.protocol.service._accounts[self.connection.identity]
        land = Selector().land(account.route["land"])
        if TYPE_CHECKING:
            assert isinstance(raw_event, GuildRoleEvent)
        guild = land.guild(raw_event.guild.id)
        role = guild.role(raw_event.role.id)
        operator = guild.member(raw_event.operator.id) if raw_event.operator else guild
        context = Context(
            account,
            operator,
            role,
            guild,
            guild.member(account.route["account"]),
        )
        return RoleDestroyed(
            context, 
            active=bool(raw_event.operator) and raw_event.operator.id == account.route["account"],
            indirect=not bool(raw_event.operator),
        )
