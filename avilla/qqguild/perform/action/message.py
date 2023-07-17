from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.ryanvk.staff import Staff
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageRevoke, MessageSend
from graia.amnesia.message import MessageChain

if TYPE_CHECKING:
    from ...account import QQGuildAccount  # noqa
    from ...protocol import QQGuildProtocol  # noqa


class QQGuildMessageActionPerform((m := AccountCollector["QQGuildProtocol", "QQGuildAccount"]())._):
    m.post_applying = True

    @MessageSend.send.collect(m, "land.guild.channel")
    async def send_group_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        result = await self.account.connection.call(
            "post",
            f"channels/{target.pattern['channel']}/messages",
            {
                # TODO: serialize message
                "content": str(message),
                "msg_id": reply.pattern["message"] if reply else None,
            }
        )
        if result is None:
            raise RuntimeError(f"Failed to send message to {target.pattern['channel']}: {message}")
        return (
            Selector()
            .land(self.account.route["land"])
            .guild(target.pattern["guild"])
            .channel(target.pattern["channel"])
            .message(result["id"])
        )
