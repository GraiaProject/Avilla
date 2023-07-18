from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.ryanvk.staff import Staff
from avilla.core.selector import Selector
from avilla.qqguild.tencent.message import form_data, pro_serialize
from avilla.standard.core.message import MessageRevoke, MessageSend
from graia.amnesia.message import MessageChain

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
        result = await self.account.connection.call(method, f"channels/{target.pattern['channel']}/messages", data)
        if result is None:
            raise RuntimeError(f"Failed to send message to {target.pattern['channel']}: {message}")
        return (
            Selector()
            .land(self.account.route["land"])
            .guild(target.pattern["guild"])
            .channel(target.pattern["channel"])
            .message(result["id"])
        )

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
            raise RuntimeError(f"Failed to send message to {target.pattern['channel']}: {message}")
        return Selector().land(self.account.route["land"]).guild(target.pattern["guild"]).message(result["id"])

    @MessageRevoke.revoke.collect(m, "lang.guild.channel")
    async def delete_msg(self, target: Selector):
        return await self.account.connection.call(
            "delete",
            f"channels/{target.pattern['channel']}/messages/{target.pattern['message']}",
            {"hidetip": str(False).lower()},
        )

    @MessageRevoke.revoke.collect(m, "lang.guild.user")
    async def delete_msg(self, target: Selector):
        return await self.account.connection.call(
            "delete",
            f"dms/{target.pattern['guild']}/messages/{target.pattern['message']}",
            {"hidetip": str(False).lower()},
        )