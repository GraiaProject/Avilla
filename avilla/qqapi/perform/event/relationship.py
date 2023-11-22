from __future__ import annotations

from avilla.core.context import Context
from avilla.core.event import RelationshipCreated, RelationshipDestroyed
from avilla.core.selector import Selector
from avilla.qqapi.capability import QQAPICapability
from avilla.qqapi.collector.connection import ConnectionCollector


class QQAPIEventRelationshipPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/qqapi::event"
    m.identify = "relationship"

    @m.entity(QQAPICapability.event_callback, event_type="guild_create")
    async def guild_create(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        guild = land.guild(str(raw_event["id"]))
        inviter = guild.member(str(raw_event["op_user_id"]))
        context = Context(
            account,
            inviter,
            guild.member(account_route["account"]),
            guild,
            guild.member(account_route["account"]),
        )
        return RelationshipCreated(context)

    @m.entity(QQAPICapability.event_callback, event_type="guild_delete")
    async def guild_delete(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        guild = land.guild(str(raw_event["id"]))
        operator = guild.member(str(raw_event["op_user_id"]))
        context = Context(
            account,
            operator,
            guild,
            guild,
            guild.member(account_route["account"]),
        )
        return RelationshipDestroyed(context, active=False)

    @m.entity(QQAPICapability.event_callback, event_type="channel_create")
    async def channel_create(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        guild = land.guild(str(raw_event["guild_id"]))
        channel = guild.channel(str(raw_event["id"]))
        operator = guild.member(str(raw_event["op_user_id"]))
        context = Context(
            account,
            operator,
            channel.member(account_route["account"]),
            channel,
            channel.member(account_route["account"]),
        )
        return RelationshipCreated(context)

    @m.entity(QQAPICapability.event_callback, event_type="channel_delete")
    async def channel_delete(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
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

    @m.entity(QQAPICapability.event_callback, event_type="guild_member_add")
    async def guild_member_add(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        guild = land.guild(str(raw_event["guild_id"]))
        user = guild.member(str(raw_event["user"]["id"]))
        operator = guild.member(str(raw_event["op_user_id"]))
        context = Context(
            account,
            operator,
            user,
            guild,
            guild.member(account_route["account"]),
        )
        return RelationshipCreated(context)

    @m.entity(QQAPICapability.event_callback, event_type="guild_member_remove")
    async def guild_member_remove(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        guild = land.guild(str(raw_event["guild_id"]))
        user = guild.member(str(raw_event["user"]["id"]))
        operator = guild.member(str(raw_event["op_user_id"]))
        if raw_event["op_user_id"] != raw_event["user"]["id"]:
            context = Context(
                account,
                operator,
                user,
                guild,
                guild.member(account_route["account"]),
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

    @m.entity(QQAPICapability.event_callback, event_type="group_add_robot")
    async def group_add_robot(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["group_openid"]))
        operator = group.member(str(raw_event["op_member_openid"]))
        context = Context(
            account,
            operator,
            group.member(account_route["account"]),
            group,
            group.member(account_route["account"]),
        )
        return RelationshipCreated(context)

    @m.entity(QQAPICapability.event_callback, event_type="group_del_robot")
    async def group_del_robot(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["group_openid"]))
        operator = group.member(str(raw_event["op_member_openid"]))
        context = Context(
            account,
            operator,
            group.member(account_route["account"]),
            group,
            group.member(account_route["account"]),
        )
        return RelationshipDestroyed(context, active=False)

    @m.entity(QQAPICapability.event_callback, event_type="friend_add")
    async def friend_add(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account

        user = Selector().land("qq").friend(str(raw_event["openid"]))
        context = Context(
            account,
            user,
            account_route,
            user,
            account_route,
        )
        return RelationshipCreated(context)

    @m.entity(QQAPICapability.event_callback, event_type="friend_del")
    async def friend_del(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account

        user = Selector().land("qq").friend(str(raw_event["openid"]))
        context = Context(
            account,
            user,
            account_route,
            user,
            account_route,
        )
        return RelationshipDestroyed(context, active=False)
