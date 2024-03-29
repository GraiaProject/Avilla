from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from graia.amnesia.builtins.memcache import Memcache, MemcacheService
from satori.model import ChannelType, Event

from avilla.core.context import Context
from avilla.core.elements import Reference
from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.satori.capability import SatoriCapability
from avilla.satori.collector.connection import ConnectionCollector
from satori.event import MessageEvent
from avilla.standard.core.message import MessageReceived, MessageSent


class SatoriEventMessagePerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/satori::event"
    m.identify = "message"

    @m.entity(SatoriCapability.event_callback, raw_event="message-created")
    async def message_create(self, raw_event: Event):
        account = self.protocol.service._accounts[self.connection.identity]
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        reply = None
        if TYPE_CHECKING:
            assert isinstance(raw_event, MessageEvent)
        if raw_event.channel.type == ChannelType.DIRECT:
            private = Selector().land(account.route["land"]).private(raw_event.channel.id)
            user = private.user(raw_event.user.id)
            context = Context(
                account,
                user,
                account.route,
                user,
                account.route,
            )
            message = await SatoriCapability(account.staff.ext({"context": context})).deserialize(
                raw_event.message.content
            )
            if message.get(Reference):
                reply = message.get_first(Reference).message
                message = message.exclude(Reference)
            msg = Message(
                id=f"{raw_event.message.id}",
                scene=private,
                sender=private,
                content=message,
                time=raw_event.timestamp,
                reply=reply,
            )
        else:
            guild = (
                Selector()
                .land(account.route["land"])
                .guild(raw_event.guild.id if raw_event.guild else "True")
            )
            channel = guild.channel(raw_event.channel.id)
            member = channel.member(
                raw_event.member.user.id if raw_event.member and raw_event.member.user else raw_event.user.id
            )
            context = Context(
                account,
                member,
                channel,
                channel,
                channel.member(account.route["account"]),
            )
            message = await SatoriCapability(account.staff.ext({"context": context})).deserialize(
                raw_event.message.content
            )
            if message.get(Reference):
                reply = message.get_first(Reference).message
                message = message.exclude(Reference)
            msg = Message(
                id=f"{raw_event.message.id}",
                scene=channel,
                sender=member,
                content=message,
                time=raw_event.timestamp,
                reply=reply,
            )
        await cache.set(
            f"satori/account({account.route['account']}).message({msg.id})", raw_event, timedelta(minutes=5)
        )
        context._collect_metadatas(msg.to_selector(), msg)
        return (
            MessageSent(context, msg, account)
            if msg.sender.last_value == raw_event.self_id
            else MessageReceived(context, msg)
        )
