from __future__ import annotations

from datetime import datetime, timedelta
from secrets import token_urlsafe

from flywheel import scoped_collect
from graia.amnesia.builtins.memcache import Memcache, MemcacheService
from graia.amnesia.message import MessageChain

from avilla.core.builtins.capability import CoreCapability
from avilla.core.context import Context
from avilla.core.elements import Reference
from avilla.core.globals import CONTEXT_CONTEXT_VAR
from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.satori.bases import InstanceOfAccount
from avilla.satori.capability import SatoriCapability
from avilla.standard.core.message import MessageSent, revoke_message, send_message


class SatoriMessageActionPerform(m := scoped_collect.env().target, InstanceOfAccount, static=True):

    @m.impl(send_message, target="land.guild.channel")
    async def send_public_message(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if reply:
            message = Reference(reply) + message
        result = await self.account.client.message_create(
            channel_id=target["channel"], content=await SatoriCapability.serialize(message)
        )
        for msg in result:
            _ctx = Context(
                self.account,
                target.member(self.account.route["account"]),
                target,
                target,
                target.member(self.account.route["account"]),
            )
            with CONTEXT_CONTEXT_VAR.use(_ctx):
                content = await SatoriCapability.deserialize(msg.content)
            content = content.exclude(Reference)
            _msg = Message(
                id=f"{msg.id}",
                scene=target,
                sender=target.member(self.account.route["account"]),
                content=content,
                time=datetime.now(),
                reply=reply,
            )
            self.protocol.post_event(MessageSent(_ctx, _msg, self.account))
        if len(result) == 1:
            return target.message(result[0].id)
        token = token_urlsafe(16)
        await cache.set(
            f"satori/account({self.account.route['account']}).messages({token})", result, timedelta(minutes=5)
        )
        return target.message(token)

    @m.impl(send_message, target="land.user")
    @m.impl(send_message, target="land.private.user")
    async def send_private_message(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if reply:
            message = Reference(reply) + message
        if target.follows("::private.user"):
            result = await self.account.client.message_create(
                channel_id=target["private"], content=await SatoriCapability.serialize(message)
            )
        else:
            result = await self.account.client.send_private_message(
                user_id=target["user"], message=await SatoriCapability.serialize(message)
            )
        for msg in result:
            _ctx = Context(
                self.account,
                self.account.route,
                target,
                target,
                self.account.route,
            )
            with CONTEXT_CONTEXT_VAR.use(_ctx):
                content = await SatoriCapability.deserialize(msg.content)
            content = content.exclude(Reference)
            _msg = Message(
                id=f"{msg.id}",
                scene=target,
                sender=self.account.route,
                content=content,
                time=datetime.now(),
                reply=reply,
            )
            self.protocol.post_event(MessageSent(_ctx, _msg, self.account))
        if len(result) == 1:
            return target.message(result[0].id)
        token = token_urlsafe(16)
        await cache.set(
            f"satori/account({self.account.route['account']}).messages({token})", result, timedelta(minutes=5)
        )
        return target.message(token)

    @m.impl(revoke_message, target="land.guild.channel.message")
    async def revoke_public_message(self, target: Selector):
        cache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if result := await cache.get(f"satori/account({self.account.route['account']}).messages({target['message']})"):
            for msg in result:
                await self.account.client.message_delete(channel_id=target["channel"], message_id=msg.id)
            return
        await self.account.client.message_delete(channel_id=target["channel"], message_id=target["message"])

    @m.impl(revoke_message, target="land.private.user.message")
    async def revoke_private_message(self, target: Selector):
        cache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if result := await cache.get(f"satori/account({self.account.route['account']}).messages({target['message']})"):
            for msg in result:
                await self.account.client.message_delete(channel_id=target["private"], message_id=msg.id)
            return
        await self.account.client.message_delete(channel_id=target["private"], message_id=target["message"])

    @m.impl(CoreCapability.pull, "land.guild.channel.message", Message)
    async def get_public_message(self, target: Selector) -> Message:
        msg = await self.account.client.message_get(
            channel_id=target["channel"],
            message_id=target["message"],
        )
        _ctx = self.account.get_context(
            target.info("::guild.channel").member(
                msg.member.user.id if msg.member and msg.member.user else self.account.route["account"]
            )
        )
        with CONTEXT_CONTEXT_VAR.use(_ctx):
            content = await SatoriCapability.deserialize(msg.content)
        reply = None
        if replys := content.get(Reference):
            reply = target.info(f"~.message({replys[0].message['message']})")
            content = content.exclude(Reference)
        return Message(
            id=f"{msg.id}",
            scene=target.info("::guild.channel"),
            sender=target.info("::guild.channel").member(
                msg.member.user.id if msg.member and msg.member.user else self.account.route["account"]
            ),
            content=content,
            time=datetime.now(),
            reply=reply,
        )

    @m.impl(CoreCapability.pull, "land.private.user.message", Message)
    async def get_private_message(self, target: Selector) -> Message:
        msg = await self.account.client.message_get(
            channel_id=target["private"],
            message_id=target["message"],
        )
        _ctx = self.account.get_context(target.info("::private.user"))
        with CONTEXT_CONTEXT_VAR.use(_ctx):
            content = await SatoriCapability.deserialize(msg.content)
        reply = None
        if replys := content.get(Reference):
            reply = target.info(f"~.message({replys[0].message['message']})")
            content = content.exclude(Reference)
        return Message(
            id=f"{msg.id}",
            scene=target.info("::private.user"),
            sender=target.info("::private.user"),
            content=content,
            time=datetime.now(),
            reply=reply,
        )
