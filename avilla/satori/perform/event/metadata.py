from __future__ import annotations

from typing import TYPE_CHECKING
from avilla.core.context import Context
from avilla.core.event import MetadataModified, ModifyDetail
from avilla.core.selector import Selector
from avilla.satori.capability import SatoriCapability
from avilla.satori.collector.connection import ConnectionCollector
from satori.event import GuildEvent, GuildMemberEvent, GuildRoleEvent
from avilla.standard.core.profile import Summary, Avatar, Nick
from satori.model import Event


class SatoriEventMetadataPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/satori::event"
    m.identify = "metadata"

    @m.entity(SatoriCapability.event_callback, raw_event="guild-updated")
    async def guild_updated(self, raw_event: Event):
        account = self.protocol.service._accounts[self.connection.identity]
        land = Selector().land(account.route["land"])
        if TYPE_CHECKING:
            assert isinstance(raw_event, GuildEvent)
        guild = land.guild(raw_event.guild.id)
        operator = guild.member(raw_event.operator.id) if raw_event.operator else guild
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
                    Summary.inh().name: ModifyDetail("set", raw_event.guild.name, None),
                },
            ),
            MetadataModified(
                context,
                guild,
                Nick,
                {
                    Nick.inh().name: ModifyDetail("set", raw_event.guild.name, None),
                    Nick.inh().nickname: ModifyDetail("set", raw_event.guild.name, None),
                },
            ),
            MetadataModified(
                context,
                guild,
                Avatar,
                {
                    Avatar.inh().url: ModifyDetail("set", raw_event.guild.avatar, None),
                },
            )
        ]

    @m.entity(SatoriCapability.event_callback, raw_event="guild-member-updated")
    async def guild_member_updated(self, raw_event: Event):
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
        return [
            MetadataModified(
                context,
                member,
                Summary,
                {
                    Summary.inh().name: ModifyDetail("set", raw_event.member.nick, None),
                },
            ),
            MetadataModified(
                context,
                member,
                Nick,
                {
                    Nick.inh().name: ModifyDetail("set", raw_event.user.name, None),
                    Nick.inh().nickname: ModifyDetail("set", raw_event.member.nick, None),
                },
            ),
            MetadataModified(
                context,
                member,
                Avatar,
                {
                    Avatar.inh().url: ModifyDetail("set", raw_event.member.avatar, None),
                },
            )
        ]

    @m.entity(SatoriCapability.event_callback, raw_event="guild-role-updated")
    async def guild_role_updated(self, raw_event: Event):
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
        return [
            MetadataModified(
                context,
                role,
                Summary,
                {
                    Summary.inh().name: ModifyDetail("set", raw_event.role.name, None),
                },
            ),
            MetadataModified(
                context,
                role,
                Nick,
                {
                    Nick.inh().name: ModifyDetail("set", raw_event.role.name, None),
                    Nick.inh().nickname: ModifyDetail("set", raw_event.role.name, None),
                },
            ),
        ]
