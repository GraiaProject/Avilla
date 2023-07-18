from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from loguru import logger

from avilla.core.context import Context
from avilla.core.elements import Notice
from avilla.core.message import Message
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.selector import Selector
from avilla.qqguild.tencent.collector.connection import ConnectionCollector
from avilla.qqguild.tencent.element import Reference
from avilla.qqguild.tencent.message import pre_deserialize
from avilla.standard.core.message import MessageReceived

if TYPE_CHECKING:
    ...


class QQGuildEventMessagePerform((m := ConnectionCollector())._):
    m.post_applying = True

    @EventParse.collect(m, "at_message_create")
    async def at_message(self, raw_event: dict):
        account_route = Selector().land("qqguild").account(self.connection.account_id)
        account = self.protocol.avilla.accounts.get(account_route)
        if account is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        guild = Selector().land("qqguild").guild(raw_event["guild_id"])
        channel = guild.channel(raw_event["channel_id"])
        author = channel.member(raw_event["author"]["id"])
        message = await account.account.staff.deserialize_message(pre_deserialize(raw_event))
        reply = None
        if i := message.get(Reference):
            reply = channel.message(i[0].message_id)
            message = message.exclude(Reference)
        ats = [Notice(channel.user(i["id"])) for i in raw_event["mentions"]]
        return MessageReceived(
            Context(
                account.account,
                author,
                channel,
                channel,
                account_route,
            ),
            Message(
                id=raw_event["id"],
                scene=channel,
                sender=author,
                content=message,
                time=datetime.fromisoformat(raw_event["timestamp"]),
                reply=reply,
            ),
        )

    @EventParse.collect(m, "message_create")
    async def message(self, raw_event: dict):
        account_route = Selector().land("qqguild").account(self.connection.account_id)
        account = self.protocol.avilla.accounts.get(account_route)
        if account is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        guild = Selector().land("qqguild").guild(raw_event["guild_id"])
        channel = guild.channel(raw_event["channel_id"])
        author = channel.member(raw_event["author"]["id"])
        message = await account.account.staff.deserialize_message(pre_deserialize(raw_event))
        reply = None
        if i := message.get(Reference):
            reply = channel.message(i[0].message_id)
            message = message.exclude(Reference)

        return MessageReceived(
            Context(
                account.account,
                author,
                channel,
                channel,
                account_route,
            ),
            Message(
                id=raw_event["id"],
                scene=channel,
                sender=author,
                content=message,
                time=datetime.fromisoformat(raw_event["timestamp"]),
                reply=reply,
            ),
        )

    @EventParse.collect(m, "direct_message_create")
    async def direct_message(self, raw_event: dict):
        account_route = Selector().land("qqguild").account(self.connection.account_id)
        account = self.protocol.avilla.accounts.get(account_route)
        if account is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        guild = Selector().land("qqguild").guild(raw_event["guild_id"])
        author = guild.user(raw_event["author"]["id"])
        message = await account.account.staff.deserialize_message(pre_deserialize(raw_event))
        reply = None
        if i := message.get(Reference):
            reply = guild.message(i[0].message_id)
            message = message.exclude(Reference)

        return MessageReceived(
            Context(
                account.account,
                author,
                author,
                author,
                account_route,
            ),
            Message(
                id=raw_event["id"],
                scene=author,
                sender=author,
                content=message,
                time=datetime.fromisoformat(raw_event["timestamp"]),
                reply=reply,
            ),
        )
