from __future__ import annotations

from flywheel import scoped_collect

from avilla.core.context import Context
from avilla.core.event import (
    MemberCreated,
    MemberDestroyed,
    SceneCreated,
    SceneDestroyed,
)
from avilla.core.selector import Selector
from avilla.satori.bases import InstanceOfAccount
from avilla.satori.capability import SatoriCapability
from avilla.satori.collector.connection import ConnectionCollector
from satori.event import GuildEvent, GuildMemberEvent, GuildRoleEvent
from avilla.satori.event import RoleCreated, RoleDestroyed


class SatoriEventRelationshipPerform(m := scoped_collect.globals().target, InstanceOfAccount, static=True):

    @m.impl(SatoriCapability.event_callback, raw_event="guild-added")
    async def guild_added(self, event: GuildEvent):
        account = self.account
        land = Selector().land(account.route["land"])
        guild = land.guild(event.guild.id)
        inviter = guild.member(event.operator.id) if event.operator else guild
        context = Context(
            account,
            inviter,
            guild,
            guild,
            guild.member(account.route["account"]),
        )
        return SceneCreated(context)

    @m.impl(SatoriCapability.event_callback, raw_event="guild-removed")
    async def guild_removed(self, event: GuildEvent):
        account = self.account
        land = Selector().land(account.route["land"])
        guild: Selector = land.guild(event.guild.id)
        operator = guild.member(event.operator.id) if event.operator else guild
        context = Context(
            account,
            operator,
            guild,
            guild,
            guild.member(account.route["account"]),
        )
        return SceneDestroyed(
            context,
            active=bool(event.operator) and event.operator.id == account.route["account"],
            indirect=not bool(event.operator),
        )

    @m.impl(SatoriCapability.event_callback, raw_event="guild-member-added")
    async def guild_member_added(self, event: GuildMemberEvent):
        account = self.account
        land = Selector().land(account.route["land"])
        guild = land.guild(event.guild.id)
        member = guild.member(event.member.user.id if event.member.user else event.user.id)
        operator = guild.member(event.operator.id) if event.operator else member
        context = Context(
            account,
            operator,
            member,
            guild,
            guild.member(account.route["account"]),
        )
        return MemberCreated(context)

    @m.impl(SatoriCapability.event_callback, raw_event="guild-member-removed")
    async def guild_member_removed(self, event: GuildMemberEvent):
        account = self.account
        land = Selector().land(account.route["land"])
        guild = land.guild(event.guild.id)
        member = guild.member(event.member.user.id if event.member.user else event.user.id)
        operator = guild.member(event.operator.id) if event.operator else member
        context = Context(
            account,
            operator,
            member,
            guild,
            guild.member(account.route["account"]),
        )
        return MemberDestroyed(
            context,
            active=bool(event.operator) and event.operator.id == member["member"],
            indirect=not bool(event.operator),
        )

    @m.impl(SatoriCapability.event_callback, raw_event="guild-role-created")
    async def guild_role_created(self, event: GuildRoleEvent):
        account = self.account
        land = Selector().land(account.route["land"])
        guild = land.guild(event.guild.id)
        role = guild.role(event.role.id)
        operator = guild.member(event.operator.id) if event.operator else guild
        context = Context(
            account,
            operator,
            role,
            guild,
            guild.member(account.route["account"]),
        )
        return RoleCreated(context)

    @m.impl(SatoriCapability.event_callback, raw_event="guild-role-deleted")
    async def guild_role_deleted(self, event: GuildRoleEvent):
        account = self.account
        land = Selector().land(account.route["land"])
        guild = land.guild(event.guild.id)
        role = guild.role(event.role.id)
        operator = guild.member(event.operator.id) if event.operator else guild
        context = Context(
            account,
            operator,
            role,
            guild,
            guild.member(account.route["account"]),
        )
        return RoleDestroyed(
            context,
            active=bool(event.operator) and event.operator.id == account.route["account"],
            indirect=not bool(event.operator),
        )
