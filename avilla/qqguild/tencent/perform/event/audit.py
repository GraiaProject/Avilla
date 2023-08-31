from __future__ import annotations

from datetime import datetime

from avilla.core.context import Context
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.selector import Selector
from avilla.qqguild.tencent.collector.connection import ConnectionCollector
from avilla.qqguild.tencent.audit import Audit, MessageAuditPass, MessageAuditReject


class QQGuildEventAuditPerform((m := ConnectionCollector())._):
    m.post_applying = True

    @EventParse.collect(m, "message_audit_pass")
    async def on_message_audit_pass(self, raw_event: dict):
        account_route = Selector().land("qqguild").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qqguild")
        guild = land.guild(str(raw_event["guild_id"]))
        channel = guild.channel(str(raw_event["channel_id"]))
        message = channel.message(str(raw_event["message_id"]))
        audit = Audit(
            raw_event["audit_id"],
            channel,
            raw_event["seq_in_channel"],
            datetime.fromtimestamp(raw_event["audit_time"]),
            datetime.fromtimestamp(raw_event["audit_time"]),
            message
        )
        context = Context(
            account,
            channel,
            channel.member(account_route["account"]),
            channel,
            channel.member(account_route["account"]),
        )
        return MessageAuditPass(context, audit)


    @EventParse.collect(m, "message_audit_reject")
    async def on_message_audit_reject(self, raw_event: dict):
        account_route = Selector().land("qqguild").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qqguild")
        guild = land.guild(str(raw_event["guild_id"]))
        channel = guild.channel(str(raw_event["channel_id"]))
        audit = Audit(
            raw_event["audit_id"],
            channel,
            raw_event["seq_in_channel"],
            datetime.fromtimestamp(raw_event["audit_time"]),
            datetime.fromtimestamp(raw_event["audit_time"]),
        )
        context = Context(
            account,
            channel,
            channel.member(account_route["account"]),
            channel,
            channel.member(account_route["account"]),
        )
        return MessageAuditReject(context, audit)
