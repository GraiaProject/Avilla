from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from graia.amnesia.message import MessageChain
from telegram import Message as TelegramMessage

from avilla.core import Context, Message
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageSend, MessageSent
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.fragments import MessageFragment, MessageFragmentReference

if TYPE_CHECKING:
    from avilla.telegram.account import TelegramAccount  # noqa
    from avilla.telegram.protocol import TelegramProtocol  # noqa


class TelegramMessageActionPerform((m := AccountCollector["TelegramProtocol", "TelegramAccount"]())._):
    m.namespace = "avilla.protocol/telegram::action"
    m.identify = "message"

    @m.entity(MessageSend.send, target="land.chat")
    @m.entity(MessageSend.send, target="land.chat.thread")
    async def send_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        s_message = await TelegramCapability(self.account.staff).serialize(message)
        if reply is not None:
            s_message.insert(0, MessageFragmentReference(reply))
        result: list[TelegramMessage] = await self.account.instance.send(target, s_message)
        d_result = [MessageFragment.decompose(m) for m in result]
        if self.account.instance.config.reformat:
            # MediaGroup may be out of order
            d_result = [MessageFragment.sort(*[frag for frags in d_result for frag in frags])]
        decomposed = [await TelegramCapability(self.account.staff).deserialize(frag) for frag in d_result]
        sent_chain = decomposed[0]
        for m in decomposed[1:]:
            sent_chain.extend(m)
        context = Context(
            account=self.account,
            client=self.account.route,
            endpoint=target,
            scene=target,
            selft=self.account.route,
        )
        message_ids = ",".join(map(str, [m.message_id for m in result]))
        event = MessageSent(
            context,
            Message(
                id=",".join(map(str, [m.message_id for m in result])),
                scene=target,
                sender=self.account.route,
                content=sent_chain,
                time=datetime.now(),
            ),
            self.account,
        )
        self.protocol.post_event(event)
        return Selector().land(self.account.route["land"]).chat(target.pattern["chat"]).message(message_ids)
