from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.context import ContextCollector
from avilla.core.ryanvk.staff import Staff
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageSend
from graia.amnesia.message import MessageChain

if TYPE_CHECKING:
    from ...account import ElizabethAccount  # noqa
    from ...protocol import ElizabethProtocol  # noqa


class ElizabethMessageActionPerform((m := ContextCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.post_applying = True

    @MessageSend.send.collect(m, "land.group")
    async def send_group_message(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        result = await self.account.connection.call(
            "update",
            "sendGroupMessage",
            {
                "target": int(target.pattern["group"]),
                "messageChain": await Staff(self.account).serialize_message(message),
                **({"quote": reply.pattern["message"]} if reply is not None else {}),
            },
        )
        if result is None:
            raise RuntimeError(f"Failed to send message to {target.pattern['group']}: {message}")
        return Selector().land(self.account.route["land"]).group(target.pattern["group"]).message(result["messageId"])
