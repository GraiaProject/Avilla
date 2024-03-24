from __future__ import annotations

from flywheel import scoped_collect

from avilla.core.context import Context
from avilla.core.event import MetadataModified, ModifyDetail
from avilla.core.selector import Selector
from avilla.satori.bases import InstanceOfAccount
from avilla.satori.capability import SatoriCapability
from avilla.satori.model import GuildEvent, GuildMemberEvent, GuildRoleEvent
from avilla.standard.core.profile import Avatar, Nick, Summary


class SatoriEventMetadataPerform(m := scoped_collect.globals().target, InstanceOfAccount, static=True):

    @m.impl(SatoriCapability.event_callback, raw_event="guild-updated")
    async def guild_updated(self, event: GuildEvent):
        account = self.account
        land = Selector().land(account.route["land"])
        guild = land.guild(event.guild.id)
        operator = guild.member(event.operator.id) if event.operator else guild
        context = Context(
            account,
            operator,
            guild,
            guild,
            guild.member(account.route["account"]),
        )
        return [
            MetadataModified(
                context,
                guild,
                Summary,
                {
                    Summary.inh().name: ModifyDetail("set", event.guild.name, None),
                },
            ),
            MetadataModified(
                context,
                guild,
                Nick,
                {
                    Nick.inh().name: ModifyDetail("set", event.guild.name, None),
                    Nick.inh().nickname: ModifyDetail("set", event.guild.name, None),
                },
            ),
            MetadataModified(
                context,
                guild,
                Avatar,
                {
                    Avatar.inh().url: ModifyDetail("set", event.guild.avatar, None),
                },
            ),
        ]

    @m.impl(SatoriCapability.event_callback, raw_event="guild-member-updated")
    async def guild_member_updated(self, event: GuildMemberEvent):
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
        return [
            MetadataModified(
                context,
                member,
                Summary,
                {
                    Summary.inh().name: ModifyDetail("set", event.member.nick, None),
                },
            ),
            MetadataModified(
                context,
                member,
                Nick,
                {
                    Nick.inh().name: ModifyDetail("set", event.user.name, None),
                    Nick.inh().nickname: ModifyDetail("set", event.member.nick, None),
                },
            ),
            MetadataModified(
                context,
                member,
                Avatar,
                {
                    Avatar.inh().url: ModifyDetail("set", event.member.avatar, None),
                },
            ),
        ]

    @m.impl(SatoriCapability.event_callback, raw_event="guild-role-updated")
    async def guild_role_updated(self, event: GuildRoleEvent):
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
        return [
            MetadataModified(
                context,
                role,
                Summary,
                {
                    Summary.inh().name: ModifyDetail("set", event.role.name, None),
                },
            ),
            MetadataModified(
                context,
                role,
                Nick,
                {
                    Nick.inh().name: ModifyDetail("set", event.role.name, None),
                    Nick.inh().nickname: ModifyDetail("set", event.role.name, None),
                },
            ),
        ]
