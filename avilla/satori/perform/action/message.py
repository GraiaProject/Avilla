from __future__ import annotations

from datetime import datetime, timedelta
from secrets import token_urlsafe
from typing import TYPE_CHECKING

from graia.amnesia.builtins.memcache import Memcache, MemcacheService
from graia.amnesia.message import MessageChain

from avilla.core.context import Context
from avilla.core.elements import Reference
from avilla.core.message import Message
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.satori.capability import SatoriCapability
from avilla.standard.core.message import MessageRevoke, MessageSend, MessageSent

if TYPE_CHECKING:
    from avilla.satori.account import SatoriAccount  # noqa
    from avilla.satori.protocol import SatoriProtocol  # noqa


class SatoriMessageActionPerform((m := AccountCollector["SatoriProtocol", "SatoriAccount"]())._):
    m.namespace = "avilla.protocol/satori::action"
    m.identify = "message"

    @m.entity(MessageSend.send, target="land.guild.channel")
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
            channel_id=target["channel"], content=await SatoriCapability(self.account.staff).serialize(message)
        )
        for msg in result:
            _ctx = Context(
                self.account,
                target.member(self.account.route["account"]),
                target,
                target,
                target.member(self.account.route["account"]),
            )
            content = await SatoriCapability(self.account.staff.ext({"context": _ctx})).deserialize(msg.content)
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

    @m.entity(MessageSend.send, target="land.user")
    @m.entity(MessageSend.send, target="land.private.user")
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
                channel_id=target["private"], content=await SatoriCapability(self.account.staff).serialize(message)
            )
        else:
            result = await self.account.client.send_private_message(
                user_id=target["user"], message=await SatoriCapability(self.account.staff).serialize(message)
            )
        for msg in result:
            _ctx = Context(
                self.account,
                self.account.route,
                target,
                target,
                self.account.route,
            )
            content = await SatoriCapability(self.account.staff.ext({"context": _ctx})).deserialize(msg.content)
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

    @m.entity(MessageRevoke.revoke, target="land.guild.channel.message")
    async def revoke_public_message(self, target: Selector):
        cache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if result := await cache.get(f"satori/account({self.account.route['account']}).messages({target['message']})"):
            for msg in result:
                await self.account.client.message_delete(channel_id=target["channel"], message_id=msg.id)
            return
        await self.account.client.message_delete(channel_id=target["channel"], message_id=target["message"])

    @m.entity(MessageRevoke.revoke, target="land.private.user.message")
    async def revoke_private_message(self, target: Selector):
        cache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if result := await cache.get(f"satori/account({self.account.route['account']}).messages({target['message']})"):
            for msg in result:
                await self.account.client.message_delete(channel_id=target["private"], message_id=msg.id)
            return
        await self.account.client.message_delete(channel_id=target["private"], message_id=target["message"])

    @m.pull("land.guild.channel.message", Message)
    async def get_public_message(self, message: Selector, route: ...) -> Message:
        msg = await self.account.client.message_get(
            channel_id=message["channel"],
            message_id=message["message"],
        )
        _ctx = self.account.get_context(
            message.info("::guild.channel").member(
                msg.member.user.id if msg.member and msg.member.user else self.account.route["account"]
            )
        )
        content = await SatoriCapability(self.account.staff.ext({"context": _ctx})).deserialize(msg.content)
        reply = None
        if replys := content.get(Reference):
            reply = message.info(f"~.message({replys[0].message['message']})")
            content = content.exclude(Reference)
        return Message(
            id=f"{msg.id}",
            scene=message.info("::guild.channel"),
            sender=message.info("::guild.channel").member(
                msg.member.user.id if msg.member and msg.member.user else self.account.route["account"]
            ),
            content=content,
            time=datetime.now(),
            reply=reply,
        )

    @m.pull("land.private.user.message", Message)
    async def get_private_message(self, message: Selector, route: ...) -> Message:
        msg = await self.account.client.message_get(
            channel_id=message["private"],
            message_id=message["message"],
        )
        _ctx = self.account.get_context(message.info("::private.user"))
        content = await SatoriCapability(self.account.staff.ext({"context": _ctx})).deserialize(msg.content)
        reply = None
        if replys := content.get(Reference):
            reply = message.info(f"~.message({replys[0].message['message']})")
            content = content.exclude(Reference)
        return Message(
            id=f"{msg.id}",
            scene=message.info("::private.user"),
            sender=message.info("::private.user"),
            content=content,
            time=datetime.now(),
            reply=reply,
        )
