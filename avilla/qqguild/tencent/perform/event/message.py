from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from loguru import logger

from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.selector import Selector
from avilla.qqguild.tencent.collector.connection import ConnectionCollector
from avilla.qqguild.tencent.element import Reference
from avilla.qqguild.tencent.utils import pre_deserialize
from avilla.standard.core.message import MessageReceived, MessageRevoked

if TYPE_CHECKING:
    ...


class QQGuildEventMessagePerform((m := ConnectionCollector())._):
    m.post_applying = True

    @EventParse.collect(m, "at_message_create")
    @EventParse.collect(m, "message_create")
    async def at_message(self, raw_event: dict):
        # TODO: put the author.bot metadata
        account_route = Selector().land("qqguild").account(self.connection.account_id)
        info = self.protocol.avilla.accounts.get(account_route)
        if info is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        account = info.account
        guild = Selector().land("qqguild").guild(raw_event["guild_id"])
        channel = guild.channel(raw_event["channel_id"])
        author = channel.member(raw_event["author"]["id"])
        context = Context(
            account,
            author,
            channel,
            channel,
            channel.member(account_route["account"]),
        )
        message = await account.staff.ext({"context": context}).deserialize_message(pre_deserialize(raw_event))
        reply = None
        if i := message.get(Reference):
            reply = channel.message(i[0].message_id)
            message = message.exclude(Reference)
        return MessageReceived(
            context,
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
        info = self.protocol.avilla.accounts.get(account_route)
        if info is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        account = info.account
        guild = Selector().land("qqguild").guild(raw_event["guild_id"])
        author = guild.user(raw_event["author"]["id"])
        context = Context(
            account,
            author,
            account_route,
            author,
            account_route,
        )
        message = await account.staff.ext({"context": context}).deserialize_message(pre_deserialize(raw_event))
        reply = None
        if i := message.get(Reference):
            reply = guild.message(i[0].message_id)
            message = message.exclude(Reference)

        return MessageReceived(
            context,
            Message(
                id=raw_event["id"],
                scene=author,
                sender=author,
                content=message,
                time=datetime.fromisoformat(raw_event["timestamp"]),
                reply=reply,
            ),
        )

    @EventParse.collect(m, "message_delete")
    @EventParse.collect(m, "public_message_delete")
    async def public_message_delete(self, raw_event: dict):
        account_route = Selector().land("qqguild").account(self.connection.account_id)
        info = self.protocol.avilla.accounts.get(account_route)
        if info is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        account = info.account
        guild = Selector().land("qqguild").guild(raw_event["message"]["guild_id"])
        channel = guild.channel(raw_event["message"]["channel_id"])
        author = channel.member(raw_event["message"]["author"]["id"])
        operator = channel.member(raw_event["op_user"]["id"])
        context = Context(
            account,
            operator,
            channel,
            channel,
            channel.member(account_route["account"]),
        )
        return MessageRevoked(context, author.message(raw_event["message"]["id"]), operator)

    @EventParse.collect(m, "direct_message_delete")
    async def direct_message_delete(self, raw_event: dict):
        account_route = Selector().land("qqguild").account(self.connection.account_id)
        info = self.protocol.avilla.accounts.get(account_route)
        if info is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        account = info.account
        guild = Selector().land("qqguild").guild(raw_event["message"]["guild_id"])
        author = guild.user(raw_event["message"]["author"]["id"])
        operator = guild.user(raw_event["op_user"]["id"])
        context = Context(
            account,
            operator,
            author,
            author,
            account_route,
        )
        return MessageRevoked(context, author.message(raw_event["message"]["id"]), operator)
