from __future__ import annotations

from avilla.core.context import Context
from avilla.core.event import MetadataModified, ModifyDetail
from avilla.core.selector import Selector
from avilla.qqapi.capability import QQAPICapability
from avilla.qqapi.collector.connection import ConnectionCollector
from avilla.standard.core.profile import Summary


class QQAPIEventMetadataPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/qqapi::event"
    m.identify = "metadata"

    @m.entity(QQAPICapability.event_callback, event_type="guild_update")
    async def guild_update(self, event_type: ..., raw_event: dict):
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
        return MetadataModified(
            context,
            guild,
            Summary,
            {
                Summary.inh().name: ModifyDetail("set", raw_event["name"], None),
                Summary.inh().description: ModifyDetail("set", raw_event["description"], None),
            },
        )

    @m.entity(QQAPICapability.event_callback, event_type="channel_update")
    async def channel_update(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        guild = land.guild(str(raw_event["guild_id"]))
        channel = guild.channel(str(raw_event["id"]))
        operator = channel.member(str(raw_event["op_user_id"]))
        context = Context(
            account,
            operator,
            channel,
            guild,
            channel.member(account_route["account"]),
        )
        return MetadataModified(
            context, channel, Summary, {Summary.inh().name: ModifyDetail("set", raw_event["name"], None)}
        )
