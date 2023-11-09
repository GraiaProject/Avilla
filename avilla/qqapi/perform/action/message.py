from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from graia.amnesia.builtins.memcache import Memcache, MemcacheService
from graia.amnesia.message import MessageChain
from loguru import logger

from avilla.core import CoreCapability, Message
from avilla.core.exceptions import ActionFailed
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.qqapi.capability import QQAPICapability
from avilla.qqapi.exception import AuditException
from avilla.qqapi.utils import form_data
from avilla.standard.core.message import (
    MessageReceived,
    MessageRevoke,
    MessageSend,
    MessageSent,
)

if TYPE_CHECKING:
    from avilla.qqapi.account import QQAPIAccount  # noqa
    from avilla.qqapi.protocol import QQAPIProtocol  # noqa


class QQAPIMessageActionPerform((m := AccountCollector["QQAPIProtocol", "QQAPIAccount"]())._):
    m.namespace = "avilla.protocol/qqapi::action"
    m.identify = "message"

    @MessageSend.send.collect(m, target="land.guild.channel")
    async def send_channel_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        msg = await QQAPICapability(self.account.staff).serialize(message)
        if event_id := await cache.get(f"qqapi/account({self.account.route['account']}):{target}"):
            msg["msg_id"] = event_id
        if reply:
            msg["msg_id"] = reply.pattern["message"]
            msg["message_reference"] = {"message_id": reply.pattern["message"]}
        method, data = form_data(msg)
        try:
            result = await self.account.connection.call_http(
                method, f"channels/{target.pattern['channel']}/messages", data
            )
            if result is None:
                raise ActionFailed(f"Failed to send message to {target.pattern['channel']}: {message}")
            event = await QQAPICapability(
                self.account.staff.ext({"connection": self.account.connection})
            ).event_callback("self_message_create", result)
            if TYPE_CHECKING:
                assert isinstance(event, MessageReceived)
            event.context = self.account.get_context(target.member(self.account.route["account"]))
            event.message.scene = target
            event.message.sender = target.member(self.account.route["account"])
            self.protocol.post_event(MessageSent(event.context, event.message, self.account))
            return event.message.to_selector()
        except AuditException as e:
            audit_res = await e.get_audit_result()
            if not audit_res or not audit_res.audit.message:
                raise ActionFailed(f"Failed to send message to {target.pattern['channel']}: {message}") from e
            result = await self.account.connection.call_http(
                "get",
                f"channels/{audit_res.audit.message.pattern['channel']}/messages/{audit_res.audit.message.pattern['message']}",
            )
            if result is None:
                logger.warning(f"Failed to get message from {audit_res.audit.message.pattern['channel']}: {message}")
                return audit_res.audit.message
            event = await QQAPICapability(
                self.account.staff.ext({"connection": self.account.connection})
            ).event_callback("self_message_create", result["message"])
            if TYPE_CHECKING:
                assert isinstance(event, MessageReceived)
            event.context = self.account.get_context(target.member(self.account.route["account"]))
            event.message.scene = target
            event.message.sender = target.member(self.account.route["account"])
            self.protocol.post_event(MessageSent(event.context, event.message, self.account))
            return event.message.to_selector()

    @MessageSend.send.collect(m, target="land.group")
    async def send_group_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        msg = await QQAPICapability(self.account.staff).serialize(message)
        if event_id := await cache.get(f"qqapi/account({self.account.route['account']}):{target}"):
            msg["msg_id"] = event_id
        if reply:
            msg["msg_id"] = reply.pattern["message"]
            msg["message_reference"] = {"message_id": reply.pattern["message"]}
        if msg.get("embed"):
            msg_type = 4
        elif msg.get("ark"):
            msg_type = 3
        elif msg.get("markdown"):
            msg_type = 2
        elif msg.get("image"):
            msg_type = 1
        else:
            msg_type = 0
        msg["timestamp"] = int(datetime.now(timezone.utc).timestamp())
        if msg_type == 1:
            result = await self.account.connection.call_http(
                "post",
                f"v2/groups/{target.pattern['group']}/files",
                {
                    "file_type": 1,
                    "url": msg["image"],
                    "srv_send_msg": True,
                },
            )
            if result is None:
                raise ActionFailed(f"Failed to send message to {target.pattern['group']}: {message}")
            return target.message(result["id"])
        msg["msg_type"] = msg_type
        method, data = form_data(msg)
        result = await self.account.connection.call_http(method, f"v2/groups/{target.pattern['group']}/messages", data)
        if result is None:
            raise ActionFailed(f"Failed to send message to {target.pattern['channel']}: {message}")
        return target.message(result["id"])

    @MessageSend.send.collect(m, target="land.friend")
    async def send_friend_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        msg = await QQAPICapability(self.account.staff).serialize(message)
        if event_id := await cache.get(f"qqapi/account({self.account.route['account']}):{target}"):
            msg["msg_id"] = event_id
        if reply:
            msg["msg_id"] = reply.pattern["message"]
            msg["message_reference"] = {"message_id": reply.pattern["message"]}
        if msg.get("embed"):
            msg_type = 4
        elif msg.get("ark"):
            msg_type = 3
        elif msg.get("markdown"):
            msg_type = 2
        elif msg.get("image"):
            msg_type = 1
        else:
            msg_type = 0
        msg["timestamp"] = int(datetime.now(timezone.utc).timestamp())
        if msg_type == 1:
            result = await self.account.connection.call_http(
                "post",
                f"v2/users/{target.pattern['friend']}/files",
                {
                    "file_type": 1,
                    "url": msg["image"],
                    "srv_send_msg": True,
                },
            )
            if result is None:
                raise ActionFailed(f"Failed to send message to {target.pattern['group']}: {message}")
            return target.message(result["id"])
        msg["msg_type"] = msg_type
        method, data = form_data(msg)
        result = await self.account.connection.call_http(method, f"v2/users/{target.pattern['friend']}/messages", data)
        if result is None:
            raise ActionFailed(f"Failed to send message to {target.pattern['channel']}: {message}")
        return target.message(result["id"])

    @MessageSend.send.collect(m, target="land.guild.user")
    async def send_direct_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        msg = await QQAPICapability(self.account.staff).serialize(message)
        if event_id := await cache.get(f"qqapi/account({self.account.route['account']}):{target}"):
            msg["msg_id"] = event_id
        if reply:
            msg["msg_id"] = reply.pattern["message"]
            msg["message_reference"] = {"message_id": reply.pattern["message"]}
        method, data = form_data(msg)
        result = await self.account.connection.call_http(method, f"dms/{target.pattern['guild']}/messages", data)
        if result is None:
            raise ActionFailed(f"Failed to send message to {target.pattern['channel']}: {message}")
        event = await QQAPICapability(self.account.staff.ext({"connection": self.account.connection})).event_callback(
            "self_direct_message_create", result
        )
        if TYPE_CHECKING:
            assert isinstance(event, MessageReceived)
        event.context = self.account.get_context(target, via=self.account.route)
        event.message.scene = target
        event.message.sender = self.account.route
        self.protocol.post_event(MessageSent(event.context, event.message, self.account))
        return event.message.to_selector()

    @MessageRevoke.revoke.collect(m, target="land.guild.channel.message")
    async def delete_msg(self, target: Selector):
        await self.account.connection.call_http(
            "delete",
            f"channels/{target.pattern['channel']}/messages/{target.pattern['message']}",
            {"hidetip": str(False).lower()},
        )

    @MessageRevoke.revoke.collect(m, target="land.guild.user.message")
    async def delete_direct_msg(self, target: Selector):
        await self.account.connection.call_http(
            "delete",
            f"dms/{target.pattern['guild']}/messages/{target.pattern['message']}",
            {"hidetip": str(False).lower()},
        )

    @m.entity(CoreCapability.pull, target="land.guild.channel.message", route=Message)
    async def get_group_message(self, target: Selector, route: ...) -> Message:
        result = await self.account.connection.call_http(
            "get",
            f"channels/{target.pattern['channel']}/messages/{target.pattern['message']}",
        )
        if result is None:
            raise RuntimeError(f"Failed to get message from {target.pattern['channel']}: {target}")
        event = await self.account.staff.ext({"connection": self.account.connection}).parse_event(
            "message_create", result
        )
        if TYPE_CHECKING:
            assert isinstance(event, MessageReceived)  # noqa
        return event.message
