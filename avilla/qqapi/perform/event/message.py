from __future__ import annotations

from datetime import datetime, timedelta

from loguru import logger

from avilla.core.context import Context
from avilla.core.elements import Notice, Text
from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.qqapi.capability import QQAPICapability
from avilla.qqapi.collector.connection import ConnectionCollector
from avilla.qqapi.element import Reference
from avilla.standard.core.message import MessageReceived, MessageRevoked
from avilla.standard.core.profile import Avatar, Nick, Summary

from graia.amnesia.builtins.memcache import Memcache, MemcacheService


class QQAPIEventMessagePerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/qqapi::event"
    m.identify = "message"

    @m.entity(QQAPICapability.event_callback, event_type="at_message_create")
    @m.entity(QQAPICapability.event_callback, event_type="message_create")
    async def at_message(self, event_type: str, raw_event: dict):
        # TODO: put the author.bot metadata
        account_route = Selector().land("qq").account(self.connection.account_id)
        info = self.protocol.avilla.accounts.get(account_route)
        if info is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
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
            reply = i[0].message
            message = message.exclude(Reference)
        if event_type == "at_message_create" and message.content and isinstance(message.content[1], Text):
            text = message.content[1].text.lstrip()  # type: ignore
            if not text:
                message.content.pop(1)
            else:
                message.content[1] = Text(text)
        msg = Message(
            id=raw_event["id"],
            scene=channel,
            sender=author,
            content=message,
            time=datetime.fromisoformat(raw_event["timestamp"]),
            reply=reply,
        )
        context.cache[context.scene.display_without_land] = raw_event["id"]
        context._collect_metadatas(
            author,
            Nick(
                raw_event["author"]["username"], raw_event["member"].get("nick", raw_event["author"]["username"]), None
            ),
            Summary(raw_event["author"]["username"], "channel member"),
            Avatar(raw_event["author"]["avatar"]),
        )
        context._collect_metadatas(msg.to_selector(), msg)
        return MessageReceived(context, msg)

    @m.entity(QQAPICapability.event_callback, event_type="group_at_message_create")
    async def group_at_message(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(self.connection.account_id)
        info = self.protocol.avilla.accounts.get(account_route)
        if info is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        account = info.account
        if "group_openid" in raw_event:
            group = Selector().land("qq").group(raw_event["group_openid"])
        else:
            group = Selector().land("qq").group(raw_event["group_id"])
        if "member_openid" in raw_event["author"]:
            author = group.member(raw_event["author"]["member_openid"])
        else:
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
        # TODO: wait for qqapi upgrade
        # if i := message.get(Reference):
        #     reply = group.message(i[0].message_id)
        #     message = message.exclude(Reference)
        message.content.insert(0, Notice(group.member(account_route["account"])))
        if message.content and isinstance(message.content[1], Text):
            text = message.content[1].text.lstrip()  # type: ignore
            if not text:
                message.content.pop(1)
            else:
                message.content[1] = Text(text)
        msg = Message(
            id=raw_event["id"],
            scene=group,
            sender=author,
            content=message,
            time=datetime.fromisoformat(raw_event["timestamp"]),
            reply=reply,
        )
        context.cache[context.scene.display_without_land] = raw_event["id"]
        context._collect_metadatas(msg.to_selector(), msg)
        return MessageReceived(context, msg)

    @m.entity(QQAPICapability.event_callback, event_type="direct_message_create")
    async def direct_message(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(self.connection.account_id)
        info = self.protocol.avilla.accounts.get(account_route)
        if info is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        account = info.account
        guild = Selector().land("qq").guild(raw_event["src_guild_id"])
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
            reply = i[0].message
            message = message.exclude(Reference)

        msg = Message(
            id=raw_event["id"],
            scene=author,
            sender=author,
            content=message,
            time=datetime.fromisoformat(raw_event["timestamp"]),
            reply=reply,
        )
        context.cache[context.scene.display_without_land] = raw_event["id"]
        context.cache[f"{context.scene.display_without_land}#dms"] = raw_event["guild_id"]
        context._collect_metadatas(
            author,
            Nick(
                raw_event["author"]["username"], raw_event["member"].get("nick", raw_event["author"]["username"]), None
            ),
            Summary(raw_event["author"]["username"], "channel member"),
            Avatar(raw_event["author"]["avatar"]),
        )
        context._collect_metadatas(msg.to_selector(), msg)
        return MessageReceived(context, msg)

    @m.entity(QQAPICapability.event_callback, event_type="c2c_message_create")
    async def c2c_message(self, event_type: ..., raw_event: dict):
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        account_route = Selector().land("qq").account(self.connection.account_id)
        info = self.protocol.avilla.accounts.get(account_route)
        if info is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        account = info.account
        if "user_openid" in raw_event["author"]:
            friend = Selector().land("qq").friend(raw_event["author"]["user_openid"])
        else:
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
            reply = i[0].message
            message = message.exclude(Reference)
        msg = Message(
            id=raw_event["id"],
            scene=friend,
            sender=friend,
            content=message,
            time=datetime.fromisoformat(raw_event["timestamp"]),
            reply=reply,
        )
        context.cache[context.scene.display_without_land] = raw_event["id"]
        await cache.set(
            f"qqapi/account({account_route['account']}):{context.scene.display_without_land}",
            raw_event["id"],
            expire=timedelta(minutes=30),
        )
        context._collect_metadatas(msg.to_selector(), msg)
        return MessageReceived(context, msg)

    @m.entity(QQAPICapability.event_callback, event_type="self_message_create")
    async def self_at_message(self, event_type: ..., raw_event: dict):
        # TODO: put the author.bot metadata
        account_route = Selector().land("qq").account(self.connection.account_id)
        info = self.protocol.avilla.accounts.get(account_route)
        if info is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
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
            reply = i[0].message
            message = message.exclude(Reference)
        msg = Message(
            id=raw_event["id"],
            scene=channel,
            sender=author,
            content=message,
            time=datetime.fromisoformat(raw_event["timestamp"]),
            reply=reply,
        )
        context._collect_metadatas(msg.to_selector(), msg)
        return MessageReceived(context, msg)

    @m.entity(QQAPICapability.event_callback, event_type="self_direct_message_create")
    async def self_direct_message(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(self.connection.account_id)
        info = self.protocol.avilla.accounts.get(account_route)
        if info is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
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
            reply = i[0].message
            message = message.exclude(Reference)

        msg = Message(
            id=raw_event["id"],
            scene=author,
            sender=author,
            content=message,
            time=datetime.fromisoformat(raw_event["timestamp"]),
            reply=reply,
        )
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
            author,
            channel,
            channel.member(account_route["account"]),
        )
        context._collect_metadatas(
            author,
            Nick(raw_event["message"]["author"]["username"], raw_event["message"]["author"]["username"], None),
            Summary(raw_event["message"]["author"]["username"], "channel member"),
            Avatar(raw_event["message"]["author"]["avatar"]),
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
        context._collect_metadatas(
            author,
            Nick(raw_event["message"]["author"]["username"], raw_event["message"]["author"]["username"], None),
            Summary(raw_event["message"]["author"]["username"], "channel member"),
            Avatar(raw_event["message"]["author"]["avatar"]),
        )
        return MessageRevoked(context, author.message(raw_event["message"]["id"]), operator)
