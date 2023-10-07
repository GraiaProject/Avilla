from __future__ import annotations

from datetime import datetime, timedelta
from typing import TypedDict
from loguru import logger

from avilla.core.context import Context
from avilla.core.message import Message, MessageChain
from avilla.core.selector import Selector
from avilla.satori.capability import SatoriCapability
from avilla.satori.element import Reply
from avilla.satori.collector.connection import ConnectionCollector
from avilla.standard.core.message import MessageReceived, MessageSent
from graia.amnesia.builtins.memcache import Memcache, MemcacheService


class MessageDeserializeResult(TypedDict):
    content: MessageChain
    source: str
    time: datetime
    reply: str | None


class SatoriEventMessagePerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/satori::event"
    m.identify = "message"

    @m.entity(SatoriCapability.event_callback, event="message-created")
    async def message_create(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return

        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        reply = None
        if raw_event["channel"]["type"] == 3:  # DIRECT
            private = Selector().land(account.route["land"]).private(raw_event["channel"]["id"])
            user = private.user(raw_event["user"]["id"])
            context = Context(
                account,
                user,
                account.route,
                user,
                account.route,
            )
            message = await SatoriCapability(account.staff.ext({"context": context})).deserialize(
                raw_event["message"]["content"]
            )
            if message.get(Reply):
                reply = user.message(message.get(Reply)[0].id)
                message = message.exclude(Reply)
            msg = Message(
                id=f'{raw_event["message"]["id"]}',
                scene=private,
                sender=private,
                content=message,
                time=datetime.fromtimestamp(raw_event["timestamp"] / 1000),
                reply=reply,
            )
        else:
            public = Selector().land(account.route["land"]).public(
                raw_event.get("guild", {}).get("id", raw_event["channel"]["id"])
            )
            channel = public.channel(raw_event["channel"]["id"])
            member = channel.member(raw_event.get("member", {}).get("id", raw_event["user"]["id"]))
            context = Context(
                account,
                member,
                channel,
                channel,
                channel.member(account.route["account"]),
            )
            message = await SatoriCapability(account.staff.ext({"context": context})).deserialize(
                raw_event["message"]["content"]
            )
            if message.get(Reply):
                reply = channel.message(message.get(Reply)[0].id)
                message = message.exclude(Reply)
            msg = Message(
                id=f'{raw_event["message"]["id"]}',
                scene=channel,
                sender=member,
                content=message,
                time=datetime.fromtimestamp(raw_event["timestamp"] / 1000),
                reply=reply,
            )
        await cache.set(f"satori/account({account.route['account']}).message({msg.id})", raw_event, timedelta(minutes=5))
        context._collect_metadatas(msg.to_selector(), msg)
        return MessageSent(
            context,
            msg,
            account
        ) if msg.sender.last_value == self_id else MessageReceived(
            context,
            msg
        )
