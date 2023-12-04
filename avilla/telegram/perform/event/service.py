from __future__ import annotations

from telegram import Update

from avilla.core.context import Context
from avilla.core.selector import Selector
from avilla.standard.telegram.event import ForumTopicClosed, ForumTopicCreated
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.collector.instance import InstanceCollector


class TelegramEventServicePerform((m := InstanceCollector())._):
    m.namespace = "avilla.protocol/telegram::event"
    m.identify = "service"

    @m.entity(TelegramCapability.event_callback, event_type="event.forum_topic_created")
    async def forum_topic_created(self, event_type: str, raw_event: Update):
        self_id = raw_event.get_bot().id
        account = self.account
        chat = (
            Selector()
            .land(account.route["land"])
            .chat(str(raw_event.message.chat.id))
            .thread(str(raw_event.message.message_thread_id))
        )
        context = Context(
            account,
            chat.member(str(raw_event.message.from_user.id)),
            chat,
            chat,
            Selector().land(account.route["land"]).account(self_id),
        )

        return ForumTopicCreated(
            context,
            message_thread_id=raw_event.message.message_thread_id,
            name=raw_event.message.forum_topic_created.name,
            icon_color=raw_event.message.forum_topic_created.icon_color,
            icon_custom_emoji_id=raw_event.message.forum_topic_created.icon_custom_emoji_id,
        )

    @m.entity(TelegramCapability.event_callback, event_type="event.forum_topic_closed")
    async def forum_topic_closed(self, event_type: str, raw_event: Update):
        self_id = raw_event.get_bot().id
        account = self.account
        chat = Selector().land(account.route["land"]).chat(str(raw_event.message.chat.id))
        context = Context(
            account,
            chat.member(str(raw_event.message.from_user.id)),
            chat,
            chat,
            Selector().land(account.route["land"]).account(self_id),
        )

        return ForumTopicClosed(context, message_thread_id=raw_event.message.message_thread_id)
