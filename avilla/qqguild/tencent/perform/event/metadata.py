from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.context import Context
from avilla.core.event import MetadataModified, ModifyDetail
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.selector import Selector
from avilla.qqguild.tencent.collector.connection import ConnectionCollector
from avilla.standard.core.profile import Summary

if TYPE_CHECKING:
    ...


class QQGuildEventMetadataPerform((m := ConnectionCollector())._):
    m.post_applying = True

    @EventParse.collect(m, "guild_update")
    async def guild_update(self, raw_event: dict):
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
        return MetadataModified(
            context,
            guild,
            Summary,
            {
                Summary.inh(lambda x: x.name): ModifyDetail("set", raw_event["name"], None),
                Summary.inh(lambda x: x.description): ModifyDetail("set", raw_event["description"], None),
            },
        )

    @EventParse.collect(m, "channel_update")
    async def channel_update(self, raw_event: dict):
        account_route = Selector().land("qqguild").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qqguild")
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
            context, channel, Summary, {Summary.inh(lambda x: x.name): ModifyDetail("set", raw_event["name"], None)}
        )
