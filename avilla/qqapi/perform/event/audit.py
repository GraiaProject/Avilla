from __future__ import annotations

from datetime import datetime

from avilla.core.context import Context
from avilla.core.selector import Selector
from avilla.qqapi.audit import Audit, MessageAuditPass, MessageAuditReject
from avilla.qqapi.capability import QQAPICapability
from avilla.qqapi.collector.connection import ConnectionCollector


class QQAPIEventAuditPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/qqapi::event"
    m.identify = "audit"

    @m.entity(QQAPICapability.event_callback, event_type="message_audit_pass")
    async def on_message_audit_pass(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        guild = land.guild(str(raw_event["guild_id"]))
        channel = guild.channel(str(raw_event["channel_id"]))
        message = channel.message(str(raw_event["message_id"]))
        audit = Audit(
            raw_event["audit_id"],
            channel,
            raw_event["seq_in_channel"],
            datetime.fromisoformat(raw_event["audit_time"]),
            datetime.fromisoformat(raw_event["audit_time"]),
            message,
        )
        context = Context(
            account,
            channel,
            channel.member(account_route["account"]),
            channel,
            channel.member(account_route["account"]),
        )
        return MessageAuditPass(context, audit)

    @m.entity(QQAPICapability.event_callback, event_type="message_audit_reject")
    async def on_message_audit_reject(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        guild = land.guild(str(raw_event["guild_id"]))
        channel = guild.channel(str(raw_event["channel_id"]))
        audit = Audit(
            raw_event["audit_id"],
            channel,
            raw_event["seq_in_channel"],
            datetime.fromisoformat(raw_event["audit_time"]),
            datetime.fromisoformat(raw_event["audit_time"]),
        )
        context = Context(
            account,
            channel,
            channel.member(account_route["account"]),
            channel,
            channel.member(account_route["account"]),
        )
        return MessageAuditReject(context, audit)
