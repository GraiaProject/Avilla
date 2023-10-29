from __future__ import annotations

from datetime import datetime, timedelta

from graia.amnesia.builtins.memcache import Memcache, MemcacheService
from loguru import logger

from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.qqapi.capability import QQAPICapability
from avilla.qqapi.collector.connection import ConnectionCollector
from avilla.qqapi.element import Reference
from avilla.standard.core.message import MessageReceived, MessageRevoked


class QQAPIEventMessagePerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/qqapi::event"
    m.identify = "message"

    @m.entity(QQAPICapability.event_callback, event_type="at_message_create")
    @m.entity(QQAPICapability.event_callback, event_type="message_create")
    async def at_message(self, event_type: ..., raw_event: dict):
        # TODO: put the author.bot metadata
        account_route = Selector().land("qq").account(self.connection.account_id)
        info = self.protocol.avilla.accounts.get(account_route)
        if info is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        account = info.account
        guild = Selector().land("qq").guild(raw_event["guild_id"])
        channel = guild.channel(raw_event["channel_id"])
        author = channel.member(raw_event["author"]["id"])
        context = Context(
            account,
            author,
            channel,
            channel,
            channel.member(account_route["account"]),
        )
        message = await QQAPICapability(account.staff.ext({"context": context})).deserialize(raw_event)
        reply = None
        if i := message.get(Reference):
            reply = channel.message(i[0].message_id)
            message = message.exclude(Reference)
        msg = Message(
            id=raw_event["id"],
            scene=channel,
            sender=author,
            content=message,
            time=datetime.fromisoformat(raw_event["timestamp"]),
            reply=reply,
        )
        await cache.set(f"qqapi/account({account_route['account']}):{channel}", raw_event["id"], timedelta(minutes=5))
        context._collect_metadatas(msg.to_selector(), msg)
        return MessageReceived(context, msg)

    @m.entity(QQAPICapability.event_callback, event_type="group_at_message_create")
    async def group_at_message(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(self.connection.account_id)
        info = self.protocol.avilla.accounts.get(account_route)
        if info is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        account = info.account
        group = Selector().land("qq").guild(raw_event["group_id"])
        author = group.member(raw_event["author"]["id"])
        context = Context(
            account,
            author,
            group,
            group,
            group.member(account_route["account"]),
        )
        message = await QQAPICapability(account.staff.ext({"context": context})).deserialize(raw_event)
        reply = None
        if i := message.get(Reference):
            reply = group.message(i[0].message_id)
            message = message.exclude(Reference)
        msg = Message(
            id=raw_event["id"],
            scene=group,
            sender=author,
            content=message,
            time=datetime.fromisoformat(raw_event["timestamp"]),
            reply=reply,
        )
        await cache.set(f"qqapi/account({account_route['account']}):{group}", raw_event["id"], timedelta(minutes=5))
        context._collect_metadatas(msg.to_selector(), msg)
        return MessageReceived(context, msg)

    @m.entity(QQAPICapability.event_callback, event_type="direct_message_create")
    async def direct_message(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(self.connection.account_id)
        info = self.protocol.avilla.accounts.get(account_route)
        if info is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        account = info.account
        guild = Selector().land("qq").guild(raw_event["guild_id"])
        author = guild.user(raw_event["author"]["id"])
        context = Context(
            account,
            author,
            account_route,
            author,
            account_route,
        )
        message = await QQAPICapability(account.staff.ext({"context": context})).deserialize(raw_event)
        reply = None
        if i := message.get(Reference):
            reply = guild.message(i[0].message_id)
            message = message.exclude(Reference)

        msg = Message(
            id=raw_event["id"],
            scene=author,
            sender=author,
            content=message,
            time=datetime.fromisoformat(raw_event["timestamp"]),
            reply=reply,
        )
        await cache.set(f"qqapi/account({account_route['account']}):{author}", raw_event["id"], timedelta(minutes=5))
        context._collect_metadatas(msg.to_selector(), msg)
        return MessageReceived(context, msg)

    @m.entity(QQAPICapability.event_callback, event_type="c2c_message_create")
    async def c2c_message(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(self.connection.account_id)
        info = self.protocol.avilla.accounts.get(account_route)
        if info is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        account = info.account
        friend = Selector().land("qq").friend(raw_event["author"]["id"])
        context = Context(
            account,
            friend,
            account_route,
            friend,
            account_route,
        )
        message = await QQAPICapability(account.staff.ext({"context": context})).deserialize(raw_event)
        reply = None
        if i := message.get(Reference):
            reply = friend.message(i[0].message_id)
            message = message.exclude(Reference)

        msg = Message(
            id=raw_event["id"],
            scene=friend,
            sender=friend,
            content=message,
            time=datetime.fromisoformat(raw_event["timestamp"]),
            reply=reply,
        )
        await cache.set(f"qqapi/account({account_route['account']}):{friend}", raw_event["id"], timedelta(minutes=5))
        context._collect_metadatas(msg.to_selector(), msg)
        return MessageReceived(context, msg)

    @m.entity(QQAPICapability.event_callback, event_type="message_delete")
    @m.entity(QQAPICapability.event_callback, event_type="public_message_delete")
    async def public_message_delete(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(self.connection.account_id)
        info = self.protocol.avilla.accounts.get(account_route)
        if info is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        account = info.account
        guild = Selector().land("qq").guild(raw_event["message"]["guild_id"])
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

    @m.entity(QQAPICapability.event_callback, event_type="direct_message_delete")
    async def direct_message_delete(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(self.connection.account_id)
        info = self.protocol.avilla.accounts.get(account_route)
        if info is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        account = info.account
        guild = Selector().land("qq").guild(raw_event["message"]["guild_id"])
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
