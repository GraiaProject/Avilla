from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core import CoreCapability, Message
from avilla.core.exceptions import ActionFailed
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.ryanvk.staff import Staff
from avilla.core.selector import Selector
from avilla.qqguild.tencent.utils import form_data, pro_serialize
from avilla.qqguild.tencent.exception import AuditException
from avilla.standard.core.message import MessageRevoke, MessageSend, MessageSent, MessageReceived
from graia.amnesia.message import MessageChain
from loguru import logger

if TYPE_CHECKING:
    from avilla.qqguild.tencent.account import QQGuildAccount  # noqa
    from avilla.qqguild.tencent.protocol import QQGuildProtocol  # noqa


class QQGuildMessageActionPerform((m := AccountCollector["QQGuildProtocol", "QQGuildAccount"]())._):
    m.post_applying = True

    @MessageSend.send.collect(m, "land.guild.channel")
    async def send_channel_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        serialize_msg = await Staff.focus(self.account).serialize_message(message)
        _data = pro_serialize(serialize_msg)
        if reply:
            _data["msg_id"] = reply.pattern["message"]
        method, data = form_data(_data)
        try:
            result = await self.account.connection.call(method, f"channels/{target.pattern['channel']}/messages", data)
            if result is None:
                raise ActionFailed(f"Failed to send message to {target.pattern['channel']}: {message}")
            event = await self.account.staff.ext({"connection": self.account.connection}).parse_event("message_create", result)
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
                raise ActionFailed(
                    f"Failed to send message to {target.pattern['channel']}: {message}"
                ) from e
            result = await self.account.connection.call(
                "get",
                f"channels/{audit_res.audit.message.pattern['channel']}/messages/{audit_res.audit.message.pattern['message']}",
            )
            if result is None:
                logger.warning(f"Failed to get message from {audit_res.audit.message.pattern['channel']}: {message}")
                return audit_res.audit.message
            event = await self.account.staff.ext({"connection": self.account.connection}).parse_event("message_create", result)
            if TYPE_CHECKING:
                assert isinstance(event, MessageReceived)
            event.context = self.account.get_context(target.member(self.account.route["account"]))
            event.message.scene = target
            event.message.sender = target.member(self.account.route["account"])
            self.protocol.post_event(MessageSent(event.context, event.message, self.account))
            return event.message.to_selector()

    @MessageSend.send.collect(m, "land.guild.user")
    async def send_direct_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        serialize_msg = await Staff.focus(self.account).serialize_message(message)
        _data = pro_serialize(serialize_msg)
        if reply:
            _data["msg_id"] = reply.pattern["message"]
        method, data = form_data(_data)
        result = await self.account.connection.call(method, f"dms/{target.pattern['guild']}/messages", data)
        if result is None:
            raise ActionFailed(f"Failed to send message to {target.pattern['channel']}: {message}")
        event = await self.account.staff.ext({"connection": self.account.connection}).parse_event("direct_message_create", result)
        if TYPE_CHECKING:
            assert isinstance(event, MessageReceived)
        event.context = self.account.get_context(target, via=self.account.route)
        event.message.scene = target
        event.message.sender = self.account.route
        self.protocol.post_event(MessageSent(event.context, event.message, self.account))
        return event.message.to_selector()

    @MessageRevoke.revoke.collect(m, "land.guild.channel.message")
    async def delete_msg(self, target: Selector):
        await self.account.connection.call(
            "delete",
            f"channels/{target.pattern['channel']}/messages/{target.pattern['message']}",
            {"hidetip": str(False).lower()},
        )

    @MessageRevoke.revoke.collect(m, "land.guild.user.message")
    async def delete_direct_msg(self, target: Selector):
        await self.account.connection.call(
            "delete",
            f"dms/{target.pattern['guild']}/messages/{target.pattern['message']}",
            {"hidetip": str(False).lower()},
        )

    @m.entity(CoreCapability.pull, "land.guild.channel.message", Message)
    async def get_group_message(self, message: Selector) -> Message:
        result = await self.account.connection.call(
            "get",
            f"channels/{message.pattern['channel']}/messages/{message.pattern['message']}",
        )
        if result is None:
            raise RuntimeError(f"Failed to get message from {message.pattern['channel']}: {message}")
        event = await self.account.staff.ext({"connection": self.account.connection}).parse_event("message_create", result)
        if TYPE_CHECKING:
            assert isinstance(event, MessageReceived)  # noqa
        return event.message
