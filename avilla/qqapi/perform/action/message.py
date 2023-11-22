from __future__ import annotations

from datetime import datetime, timezone, timedelta
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
        if media := msg.get("media"):
            msg[media[0]] = media[1]
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
            event.message.content = message
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
        if "file_image" in msg:
            raise NotImplementedError("file_image is not supported yet")
        if msg.get("embed"):
            msg_type = 4
        elif msg.get("ark"):
            msg_type = 3
        elif msg.get("markdown"):
            msg_type = 2
        elif msg.get("media"):
            msg_type = 7
        else:
            msg_type = 0
        msg["timestamp"] = int(datetime.now(timezone.utc).timestamp())
        if msg_type == 7:
            file_types = {"image": 1, "video": 2, "audio": 3}
            result = await self.account.connection.call_http(
                "post",
                f"v2/groups/{target.pattern['group']}/files",
                {
                    "file_type": file_types.get(msg["media"][0], 1),
                    "url": msg["media"][1],
                    "srv_send_msg": "msg_id" not in msg,
                },
            )
            if result is None:
                raise ActionFailed(f"Failed to send message to {target.pattern['group']}: {message}")
            if "msg_id" not in msg:
                context = self.account.get_context(target)
                msg = Message(
                    result.get("id", "UNKNOWN"),
                    target,
                    target.member(self.account.route["account"]),
                    message,
                    datetime.now(timezone.utc),
                )
                self.protocol.post_event(MessageSent(context, msg, self.account))
                return target.message(result.get("id", "UNKNOWN"))
            msg["media"] = {"file_info": result["file_info"]}
            if "content" not in msg or not msg["content"]:
                msg["content"] = " "
        msg["msg_type"] = msg_type

        if seq := await cache.get(f"qqapi/account({self.account.route['account']}):{target}+msg_id:{msg.get('msg_id', '_')}"):
            msg["msg_seq"] = seq
            await cache.set(
                f"qqapi/account({self.account.route['account']}):{target}+msg_id:{msg.get('msg_id', '_')}",
                seq+1,
                expire=timedelta(minutes=5)
            )
        else:
            msg["msg_seq"] = 1
            await cache.set(
                f"qqapi/account({self.account.route['account']}):{target}+msg_id:{msg.get('msg_id', '_')}",
                2,
                expire=timedelta(minutes=5)
            )
        method, data = form_data(msg)
        result = await self.account.connection.call_http(method, f"v2/groups/{target.pattern['group']}/messages", data)
        if result is None:
            raise ActionFailed(f"Failed to send message to {target.pattern['channel']}: {message}")
        context = self.account.get_context(target)
        msg = Message(
            result.get("id", "UNKNOWN"),
            target,
            target.member(self.account.route["account"]),
            message,
            datetime.now(timezone.utc),
        )
        self.protocol.post_event(MessageSent(context, msg, self.account))
        return target.message(result.get("id", "UNKNOWN"))

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
        if "file_image" in msg:
            raise NotImplementedError("file_image is not supported yet")
        if msg.get("embed"):
            msg_type = 4
        elif msg.get("ark"):
            msg_type = 3
        elif msg.get("markdown"):
            msg_type = 2
        elif msg.get("media"):
            msg_type = 1
        else:
            msg_type = 0
        msg["timestamp"] = int(datetime.now(timezone.utc).timestamp())
        if msg_type == 1:
            file_types = {"image": 1, "video": 2, "audio": 3}
            result = await self.account.connection.call_http(
                "post",
                f"v2/users/{target.pattern['friend']}/files",
                {
                    "file_type": file_types.get(msg["media"][0], 1),
                    "url": msg["media"][1],
                    "srv_send_msg": "msg_id" not in msg,
                },
            )
            if result is None:
                raise ActionFailed(f"Failed to send message to {target.pattern['group']}: {message}")
            if "msg_id" not in msg:
                context = self.account.get_context(target)
                msg = Message(
                    result.get("id", "UNKNOWN"),
                    target,
                    target.member(self.account.route["account"]),
                    message,
                    datetime.now(timezone.utc),
                )
                self.protocol.post_event(MessageSent(context, msg, self.account))
                return target.message(result.get("id", "UNKNOWN"))
            msg["media"] = {"file_info": result["file_info"]}
            if "content" not in msg or not msg["content"]:
                msg["content"] = " "
        msg["msg_type"] = msg_type
        if "file_image" in msg:
            raise NotImplementedError("file_image is not supported yet")
        if seq := await cache.get(f"qqapi/account({self.account.route['account']}):{target}+msg_id:{msg.get('msg_id', '_')}"):
            msg["msg_seq"] = seq
            await cache.set(
                f"qqapi/account({self.account.route['account']}):{target}+msg_id:{msg.get('msg_id', '_')}",
                seq+1,
                expire=timedelta(minutes=5)
            )
        else:
            msg["msg_seq"] = 1
            await cache.set(
                f"qqapi/account({self.account.route['account']}):{target}+msg_id:{msg.get('msg_id', '_')}",
                2,
                expire=timedelta(minutes=5)
            )
        method, data = form_data(msg)
        result = await self.account.connection.call_http(method, f"v2/users/{target.pattern['friend']}/messages", data)
        if result is None:
            raise ActionFailed(f"Failed to send message to {target.pattern['channel']}: {message}")
        context = self.account.get_context(target)
        msg = Message(
            result.get("id", "UNKNOWN"),
            target,
            target.member(self.account.route["account"]),
            message,
            datetime.now(timezone.utc),
        )
        self.protocol.post_event(MessageSent(context, msg, self.account))
        return target.message(result.get("id", "UNKNOWN"))

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
        if media := msg.get("media"):
            msg[media[0]] = media[1]
        method, data = form_data(msg)
        result = await self.account.connection.call_http(method, f"dms/{target.pattern['guild']}/messages", data)
        if result is None:
            raise ActionFailed(f"Failed to send message to {target.pattern['channel']}: {message}")
        event = await QQAPICapability(self.account.staff.ext({"connection": self.account.connection})).event_callback(
            "self_direct_message_create", result
        )
        if TYPE_CHECKING:
            assert isinstance(event, MessageReceived)
        event.context = self.account.get_context(target)
        event.message.scene = target
        event.message.content = message
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
        event = await QQAPICapability(self.account.staff.ext({"connection": self.account.connection})).event_callback(
            "message_create", result
        )
        if TYPE_CHECKING:
            assert isinstance(event, MessageReceived)  # noqa
        return event.message
