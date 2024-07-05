from __future__ import annotations

from base64 import b64encode
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

from graia.amnesia.builtins.memcache import Memcache, MemcacheService
from graia.amnesia.message import MessageChain
from loguru import logger

from avilla.core import Context, CoreCapability, Message
from avilla.core.exceptions import ActionFailed
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.qqapi.capability import QQAPICapability
from avilla.qqapi.exception import AuditException
from avilla.qqapi.utils import form_data, unescape
from avilla.standard.core.message import (
    MessageReceived,
    MessageRevoke,
    MessageSend,
    MessageSent,
)
from graia.ryanvk import OptionalAccess

if TYPE_CHECKING:
    from avilla.qqapi.account import QQAPIAccount  # noqa
    from avilla.qqapi.protocol import QQAPIProtocol  # noqa


class QQAPIMessageActionPerform((m := AccountCollector["QQAPIProtocol", "QQAPIAccount"]())._):
    m.namespace = "avilla.protocol/qqapi::action"
    m.identify = "message"

    context: OptionalAccess[Context] = OptionalAccess()

    @m.entity(QQAPICapability.post_file, target="land.group")
    async def post_group_file(
        self,
        target: Selector,
        file_type: int,
        url: str | None = None,
        srv_send_msg: bool = True,
        file_data: str | bytes | None = None,
    ) -> dict:
        if isinstance(file_data, bytes):
            file_data = b64encode(file_data).decode()
        result = await self.account.connection.call_http(
            "post",
            f"v2/groups/{target.pattern['group']}/files",
            {
                "file_type": file_type,
                "url": url,
                "srv_send_msg": srv_send_msg,
                "file_data": file_data,
            },
        )
        if result is None:
            raise ActionFailed(f"Failed to post file to {target.pattern['group']}")
        return result

    @m.entity(QQAPICapability.post_file, target="land.friend")
    async def post_friend_file(
        self,
        target: Selector,
        file_type: int,
        url: str | None = None,
        srv_send_msg: bool = True,
        file_data: str | bytes | None = None,
    ) -> dict:
        if isinstance(file_data, bytes):
            file_data = b64encode(file_data).decode()
        result = await self.account.connection.call_http(
            "post",
            f"v2/users/{target.pattern['friend']}/files",
            {
                "file_type": file_type,
                "url": url,
                "srv_send_msg": srv_send_msg,
                "file_data": file_data,
            },
        )
        if result is None:
            raise ActionFailed(f"Failed to post file to {target.pattern['friend']}")
        return result

    @staticmethod
    def _extract_qq_media(msg: dict) -> dict[str, Any]:
        kwargs = {}
        if media := msg.get("media"):
            kwargs["file_type"] = {"image": 1, "video": 2, "audio": 3, "file": 4}.get(media[0], 4)
            kwargs["url"] = media[1]
        elif "file_image" in msg:
            kwargs["file_type"] = 1
            kwargs["file_data"] = msg.pop("file_image")
        elif "file_audio" in msg:
            kwargs["file_type"] = 2
            kwargs["file_data"] = msg.pop("file_audio")
        elif "file_video" in msg:
            kwargs["file_type"] = 3
            kwargs["file_data"] = msg.pop("file_video")
        elif "file_file" in msg:
            kwargs["file_type"] = 4
            kwargs["file_data"] = msg.pop("file_file")
        return kwargs

    @MessageSend.send.collect(m, target="land.guild.channel")
    async def send_channel_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        context = self.context
        msg = await QQAPICapability(self.account.staff).serialize(message)
        if context and (event_id := context.cache.get(target.display_without_land)):
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
        context = self.context
        if context and (event_id := await cache.get(f"qqapi/account({self.account.route['account']}):{context.scene.display_without_land}")):
            msg["msg_id"] = event_id
        elif context and (event_id := context.cache.get(target.display_without_land)):
            msg["msg_id"] = event_id
        if reply:
            msg["msg_id"] = reply.pattern["message"]
            # TODO: wait for api upgrade
            # msg["message_reference"] = {"message_id": reply.pattern["message"]}
        if msg.get("embed"):
            msg_type = 4
        elif msg.get("ark"):
            msg_type = 3
        elif msg.get("markdown"):
            msg_type = 2
        elif any(
            i in msg
            for i in (
                "media",
                "file_image",
                "file_video",
                "file_audio",
                "file_file",
            )
        ):
            msg_type = 7
        else:
            msg_type = 0
        msg["timestamp"] = int(datetime.now(timezone.utc).timestamp())
        if msg_type == 7:
            result = await self.post_group_file(target, srv_send_msg="msg_id" not in msg, **self._extract_qq_media(msg))
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

        if seq := await cache.get(
            f"qqapi/account({self.account.route['account']}):{target}+msg_id:{msg.get('msg_id', '_')}"
        ):
            msg["msg_seq"] = seq
            await cache.set(
                f"qqapi/account({self.account.route['account']}):{target}+msg_id:{msg.get('msg_id', '_')}",
                seq + 1,
                expire=timedelta(minutes=5),
            )
        else:
            msg["msg_seq"] = 1
            await cache.set(
                f"qqapi/account({self.account.route['account']}):{target}+msg_id:{msg.get('msg_id', '_')}",
                2,
                expire=timedelta(minutes=5),
            )
        # TODO: wait for api upgrade
        # msg["content"] = unescape(msg["content"])
        method, data = form_data(msg)
        try:
            result = await self.account.connection.call_http(method, f"v2/groups/{target.pattern['group']}/messages", data)
        except ActionFailed:
            msg["msg_seq"] = msg["msg_seq"] + (hash(target.pattern['group']) % 0x7FFFFFF) + int(datetime.now(timezone.utc).timestamp())
            result = await self.account.connection.call_http(method, f"v2/groups/{target.pattern['group']}/messages", data)
        if result is None:
            raise ActionFailed(f"Failed to send message to {target.pattern['group']}: {message}")
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
        context = self.context
        msg = await QQAPICapability(self.account.staff).serialize(message)
        if context and (event_id := context.cache.get(target.display_without_land)):
            msg["msg_id"] = event_id
        if reply:
            msg["msg_id"] = reply.pattern["message"]
            # TODO: wait for api upgrade
            # msg["message_reference"] = {"message_id": reply.pattern["message"]}
        if msg.get("embed"):
            msg_type = 4
        elif msg.get("ark"):
            msg_type = 3
        elif msg.get("markdown"):
            msg_type = 2
        elif any(
            i in msg
            for i in (
                "media",
                "file_image",
                "file_video",
                "file_audio",
                "file_file",
            )
        ):
            msg_type = 7
        else:
            msg_type = 0
        msg["timestamp"] = int(datetime.now(timezone.utc).timestamp())
        if msg_type == 7:
            result = await self.post_friend_file(target, srv_send_msg="msg_id" not in msg, **self._extract_qq_media(msg))
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
        if seq := await cache.get(
            f"qqapi/account({self.account.route['account']}):{target}+msg_id:{msg.get('msg_id', '_')}"
        ):
            msg["msg_seq"] = seq
            await cache.set(
                f"qqapi/account({self.account.route['account']}):{target}+msg_id:{msg.get('msg_id', '_')}",
                seq + 1,
                expire=timedelta(minutes=5),
            )
        else:
            msg["msg_seq"] = 1
            await cache.set(
                f"qqapi/account({self.account.route['account']}):{target}+msg_id:{msg.get('msg_id', '_')}",
                2,
                expire=timedelta(minutes=5),
            )
        # TODO: wait for api upgrade
        msg["content"] = unescape(msg["content"])
        method, data = form_data(msg)
        try:
            result = await self.account.connection.call_http(method, f"v2/users/{target.pattern['friend']}/messages", data)
        except ActionFailed:
            msg["msg_seq"] = msg["msg_seq"] + (hash(target.pattern['friend']) % 0x7FFFFFF) + int(datetime.now(timezone.utc).timestamp())
            result = await self.account.connection.call_http(method, f"v2/users/{target.pattern['friend']}/messages", data)
        if result is None:
            raise ActionFailed(f"Failed to send message to {target.pattern['friend']}: {message}")
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

    @QQAPICapability.create_dms.collect(m, target="land.guild.user")
    async def create_dms_user(self, target: Selector) -> Selector:
        result = await self.account.connection.call_http(
            "post",
            "users/@me/dms",
            {
                "recipient_id": target.pattern["user"],
                "source_guild_id": target.pattern["guild"],
            },
        )
        context = self.context
        if context:
            context.cache[f"{context.scene.display_without_land}#dms"] = result["guild_id"]
        return target.into(f"land.guild({result['guild_id']})")

    @QQAPICapability.create_dms.collect(m, target="land.guild.member")
    @QQAPICapability.create_dms.collect(m, target="land.guild.channel.member")
    async def create_dms_member(self, target: Selector) -> Selector:
        result = await self.account.connection.call_http(
            "post",
            "users/@me/dms",
            {
                "recipient_id": target.pattern["member"],
                "source_guild_id": target.pattern["guild"],
            },
        )
        context = self.context
        if context:
            context.cache[f"{context.scene.display_without_land}#dms"] = result["guild_id"]
        return target.into(f"land.guild({result['guild_id']})")

    @MessageSend.send.collect(m, target="land.guild.user")
    async def send_direct_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        context = self.context
        msg = await QQAPICapability(self.account.staff).serialize(message)
        if not context or not (send_guild_id := context.cache.get(f"{context.scene.display_without_land}#dms")):
            send_guild_id = (await self.create_dms_user(target)).pattern["guild"]
        if context and (event_id := context.cache.get(target.display_without_land)):
            msg["msg_id"] = event_id
        if reply:
            msg["msg_id"] = reply.pattern["message"]
            msg["message_reference"] = {"message_id": reply.pattern["message"]}
        if media := msg.get("media"):
            msg[media[0]] = media[1]
        method, data = form_data(msg)
        result = await self.account.connection.call_http(method, f"dms/{send_guild_id}/messages", data)
        if result is None:
            raise ActionFailed(f"Failed to send message to {target.pattern['user']}: {message}")
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
        context = self.context
        if not context or not (send_guild_id := context.cache.get(f"{context.scene.display_without_land}#dms")):
            send_guild_id = (await self.create_dms_user(target)).pattern["guild"]
            if context:
                context.cache.pop(f"{context.scene.display_without_land}#dms", None)  # type: ignore
        await self.account.connection.call_http(
            "delete",
            f"dms/{send_guild_id}/messages/{target.pattern['message']}",
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
