from __future__ import annotations

from telegram import Update

from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageReceived
from avilla.telegram.collector.instance import InstanceCollector
from avilla.telegram.elements import MessageFragment


class TelegramEventMessagePerform((m := InstanceCollector())._):
    m.post_applying = True

    @EventParse.collect(m, "message.private")
    async def message_private(self, raw_event: Update):
        self_id = raw_event.get_bot().id
        account = self.account
        chat = Selector().land(account.route["land"]).chat(str(raw_event.message.from_user.id))
        context = Context(
            account,
            chat,
            chat,
            chat,
            Selector().land(account.route["land"]).account(self_id),
        )
        message = await account.staff.ext({"context": context}).deserialize_message(
            MessageFragment.decompose(raw_event)
        )
        reply = raw_event.message.reply_to_message

        return MessageReceived(
            context,
            Message(
                id=str(raw_event.message.message_id),
                scene=chat,
                sender=chat,
                content=message,
                time=raw_event.message.date,
                reply=reply,
            ),
        )

    @EventParse.collect(m, "message.group")
    async def message_group(self, raw_event: Update):
        self_id = raw_event.get_bot().id
        account = self.account
        chat = Selector().land(account.route["land"]).chat(str(raw_event.message.chat.id))
        member = chat.member(raw_event.message.from_user.id)
        context = Context(
            account,
            member,
            chat,
            chat,
            chat.member(str(self_id)),
        )
        message = await account.staff.ext({"context": context}).deserialize_message(
            MessageFragment.decompose(raw_event)
        )
        reply = raw_event.message.reply_to_message
        return MessageReceived(
            context,
            Message(
                id=str(raw_event.message.message_id),
                scene=chat,
                sender=member,
                content=message,
                time=raw_event.message.date,
                reply=reply,
            ),
        )
