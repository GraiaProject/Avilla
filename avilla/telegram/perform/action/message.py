from __future__ import annotations

from typing import TYPE_CHECKING

from graia.amnesia.message import MessageChain

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageSend

if TYPE_CHECKING:
    from ...account import OneBot11Account  # noqa
    from ...protocol import OneBot11Protocol  # noqa


class TelegramMessageActionPerform((m := AccountCollector["TelegramProtocol", "TelegramAccount"]())._):
    m.post_applying = True

    @MessageSend.send.collect(m, "land.chat")
    async def send_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        message = await self.account.staff.serialize_message(message)
        result = await self.account.instance.send(target, message)
        return Selector().land(self.account.route["land"]).chat(target.pattern["chat"]).message(result)
