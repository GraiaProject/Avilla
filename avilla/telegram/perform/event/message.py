from __future__ import annotations

from graia.amnesia.builtins.memcache import Memcache, MemcacheService
from telegram import Update

from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageReceived
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.collector.instance import InstanceCollector
from avilla.telegram.fragments import MessageFragment


class TelegramEventMessagePerform((m := InstanceCollector())._):
    m.namespace = "avilla.protocol/telegram::event"
    m.identify = "message"

    @m.entity(TelegramCapability.event_callback, event_type="message.private")
    @m.entity(TelegramCapability.event_callback, event_type="message.group")
    @m.entity(TelegramCapability.event_callback, event_type="message.supergroup")
    async def message_private(self, event_type: str, raw_event: Update):
        self_id = raw_event.get_bot().id
        account = self.account
        chat = Selector().land(account.route["land"]).chat(str(raw_event.message.chat.id))
        if chat == "message.supergroup" and raw_event.message.message_thread_id:
            chat = chat.thread(str(raw_event.message.message_thread_id))
        context = Context(
            account,
            chat.member(raw_event.message.from_user.id) if event_type == "message.private" else chat,
            chat,
            chat,
            Selector().land(account.route["land"]).account(self_id)
            if event_type == "message.private"
            else chat.member(str(self_id)),
        )
        if media_group_id := raw_event.message.media_group_id:
            cache: Memcache = self.instance.protocol.avilla.launch_manager.get_component(MemcacheService).cache
            cached = await cache.get(f"telegram/update(media_group):{media_group_id}")
            decomposed = MessageFragment.sort(*cached)
        else:
            decomposed = MessageFragment.decompose(raw_event.message, raw_event)
        message = await TelegramCapability(account.staff.ext({"context": context})).deserialize(decomposed)
        reply = raw_event.message.reply_to_message

        return MessageReceived(
            context,
            Message(
                id=str(raw_event.message.message_id),
                scene=chat,
                sender=chat.member(raw_event.message.from_user.id) if event_type == "message.private" else chat,
                content=message,
                time=raw_event.message.date,
                reply=reply,
            ),
        )
