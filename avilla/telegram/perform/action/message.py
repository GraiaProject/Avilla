from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from graia.amnesia.message import MessageChain

from avilla.core import Context, Message
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageSend, MessageSent

if TYPE_CHECKING:
    from avilla.telegram.account import TelegramAccount  # noqa
    from avilla.telegram.protocol import TelegramProtocol  # noqa


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
        context = Context(
            account=self.account,
            client=self.account.route,
            endpoint=target,
            scene=target,
            selft=self.account.route,
        )
        event = MessageSent(
            context,
            Message(
                id=",".join(map(str, result)),
                scene=target,
                sender=self.account.route,
                content=message,
                time=datetime.now(),
            ),
            self.account,
        )
        self.protocol.post_event(event)
        return Selector().land(self.account.route["land"]).chat(target.pattern["chat"]).message(result)