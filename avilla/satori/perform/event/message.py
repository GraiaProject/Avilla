from __future__ import annotations

from datetime import timedelta

from flywheel import scoped_collect
from graia.amnesia.builtins.memcache import Memcache, MemcacheService
from satori.model import ChannelType

from avilla.core.context import Context
from avilla.core.elements import Reference
from avilla.core.globals import CONTEXT_CONTEXT_VAR
from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.satori.bases import InstanceOfAccount
from avilla.satori.capability import SatoriCapability
from avilla.satori.model import MessageEvent
from avilla.standard.core.message import MessageReceived, MessageSent


class SatoriEventMessagePerform(m := scoped_collect.globals().target, InstanceOfAccount, static=True):

    @m.impl(SatoriCapability.event_callback, raw_event="message-created")
    async def message_create(self, event: MessageEvent):
        account = self.account
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        reply = None
        if event.channel.type == ChannelType.DIRECT:
            private = Selector().land(account.route["land"]).private(event.channel.id)
            user = private.user(event.user.id)
            context = Context(
                account,
                user,
                account.route,
                user,
                account.route,
            )
            with CONTEXT_CONTEXT_VAR.use(context):
                message = await SatoriCapability.deserialize(event.message.content)
            if message.get(Reference):
                reply = message.get_first(Reference).message
                message = message.exclude(Reference)
            msg = Message(
                id=f"{event.message.id}",
                scene=private,
                sender=private,
                content=message,
                time=event.timestamp,
                reply=reply,
            )
        else:
            guild = Selector().land(account.route["land"]).guild(event.guild.id if event.guild else "True")
            channel = guild.channel(event.channel.id)
            member = channel.member(event.member.user.id if event.member and event.member.user else event.user.id)
            context = Context(
                account,
                member,
                channel,
                channel,
                channel.member(account.route["account"]),
            )
            with CONTEXT_CONTEXT_VAR.use(context):
                message = await SatoriCapability.deserialize(event.message.content)
            if message.get(Reference):
                reply = message.get_first(Reference).message
                message = message.exclude(Reference)
            msg = Message(
                id=f"{event.message.id}",
                scene=channel,
                sender=member,
                content=message,
                time=event.timestamp,
                reply=reply,
            )
        await cache.set(f"satori/account({account.route['account']}).message({msg.id})", event, timedelta(minutes=5))
        context._collect_metadatas(msg.to_selector(), msg)
        return (
            MessageSent(context, msg, account)
            if msg.sender.last_value == event.self_id
            else MessageReceived(context, msg)
        )
