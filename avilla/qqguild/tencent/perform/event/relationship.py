from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.context import Context
from avilla.core.event import RelationshipCreated, RelationshipDestroyed
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.selector import Selector
from avilla.qqguild.tencent.collector.connection import ConnectionCollector

if TYPE_CHECKING:
    ...


class QQGuildEventRelationshipPerform((m := ConnectionCollector())._):
    m.post_applying = True

    @EventParse.collect(m, "guild_create")
    async def guild_create(self, raw_event: dict):
        account_route = Selector().land("qqguild").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qqguild")
        guild = land.guild(str(raw_event["id"]))
        inviter = guild.user(str(raw_event["op_user_id"]))
        context = Context(
            account,
            guild.user(account_route["account"]),
            guild,
            guild,
            guild.user(account_route["account"]),
            mediums=[inviter] if inviter else None,
        )
        return RelationshipCreated(context)

    @EventParse.collect(m, "guild_delete")
    async def guild_delete(self, raw_event: dict):
        account_route = Selector().land("qqguild").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qqguild")
        guild = land.guild(str(raw_event["id"]))
        operator = guild.user(str(raw_event["op_user_id"]))
        context = Context(
            account,
            operator,
            guild,
            guild,
            guild.user(account_route["account"]),
        )
        return RelationshipDestroyed(context, active=False)

    @EventParse.collect(m, "channel_create")
    async def channel_create(self, raw_event: dict):
        account_route = Selector().land("qqguild").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qqguild")
        guild = land.guild(str(raw_event["guild_id"]))
        channel = guild.channel(str(raw_event["id"]))
        operator = guild.member(str(raw_event["op_user_id"]))
        context = Context(
            account,
            operator,
            channel,
            channel,
            channel.member(account_route["account"]),
        )
        return RelationshipCreated(context)

    @EventParse.collect(m, "channel_delete")
    async def channel_delete(self, raw_event: dict):
        account_route = Selector().land("qqguild").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qqguild")
        guild = land.guild(str(raw_event["guild_id"]))
        channel = guild.channel(str(raw_event["id"]))
        operator = guild.member(str(raw_event["op_user_id"]))
        context = Context(
            account,
            operator,
            channel,
            channel,
            channel.member(account_route["account"]),
        )
        return RelationshipDestroyed(context, active=False)

    @EventParse.collect(m, "guild_member_add")
    async def guild_member_add(self, raw_event: dict):
        account_route = Selector().land("qqguild").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qqguild")
        guild = land.guild(str(raw_event["guild_id"]))
        user = guild.user(str(raw_event["user"]["id"]))
        operator = guild.user(str(raw_event["operator_id"]))
        context = Context(
            account,
            user,
            guild,
            guild,
            guild.user(account_route["account"]),
            mediums=[operator],
        )
        return RelationshipCreated(context)

    @EventParse.collect(m, "guild_member_remove")
    async def guild_member_remove(self, raw_event: dict):
        account_route = Selector().land("qqguild").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qqguild")
        guild = land.guild(str(raw_event["guild_id"]))
        user = guild.user(str(raw_event["user"]["id"]))
        operator = guild.user(str(raw_event["operator_id"]))
        if raw_event["operator_id"] != raw_event["user"]["id"]:
            context = Context(
                account,
                user,
                guild,
                guild,
                guild.user(account_route["account"]),
                mediums=[operator],
            )
            return RelationshipDestroyed(context, active=False)
        else:
            context = Context(
                account,
                user,
                guild,
                guild,
                guild.user(account_route["account"]),
            )
            return RelationshipDestroyed(context, active=True)
