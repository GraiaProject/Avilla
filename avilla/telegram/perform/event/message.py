from __future__ import annotations

from graia.amnesia.builtins.memcache import Memcache, MemcacheService
from telegram import Update

from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageReceived
from avilla.standard.telegram.event import (
    ForumTopicClosed,
    ForumTopicCreated,
    ForumTopicEdited,
    ForumTopicReopened,
    GeneralForumTopicHidden,
    GeneralForumTopicUnhidden,
    VideoChatEnded,
    VideoChatParticipantsInvited,
    VideoChatScheduled,
    VideoChatStarted,
)
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
            target=chat,
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

        return ForumTopicClosed(context, target=chat)

    @m.entity(TelegramCapability.event_callback, event_type="event.forum_topic_edited")
    async def forum_topic_edited(self, event_type: str, raw_event: Update):
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

        return ForumTopicEdited(
            context,
            target=chat,
            name=raw_event.message.forum_topic_created.name,
            icon_custom_emoji_id=raw_event.message.forum_topic_created.icon_custom_emoji_id,
        )

    @m.entity(TelegramCapability.event_callback, event_type="event.forum_topic_reopened")
    async def forum_topic_reopened(self, event_type: str, raw_event: Update):
        self_id = raw_event.get_bot().id
        account = self.account
        chat = Selector().land(account.route["land"]).chat(str(raw_event.message.chat.id))
        if thread_id := raw_event.message.message_thread_id:
            chat = chat.thread(str(thread_id))
        context = Context(
            account,
            chat.member(str(raw_event.message.from_user.id)),
            chat,
            chat,
            Selector().land(account.route["land"]).account(self_id),
        )

        return ForumTopicReopened(context, target=chat)

    @m.entity(TelegramCapability.event_callback, event_type="event.general_forum_topic_hidden")
    async def general_forum_topic_hidden(self, event_type: str, raw_event: Update):
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

        return GeneralForumTopicHidden(context, target=chat)

    @m.entity(TelegramCapability.event_callback, event_type="event.general_forum_topic_unhidden")
    async def general_forum_topic_unhidden(self, event_type: str, raw_event: Update):
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

        return GeneralForumTopicUnhidden(context, target=chat)

    @m.entity(TelegramCapability.event_callback, event_type="event.video_chat_ended")
    async def video_chat_ended(self, event_type: str, raw_event: Update):
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

        return VideoChatEnded(context, target=chat, duration=raw_event.message.video_chat_ended.duration)

    @m.entity(TelegramCapability.event_callback, event_type="event.video_chat_started")
    async def video_chat_started(self, event_type: str, raw_event: Update):
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

        return VideoChatStarted(context, target=chat)

    @m.entity(TelegramCapability.event_callback, event_type="event.video_chat_scheduled")
    async def video_chat_scheduled(self, event_type: str, raw_event: Update):
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

        return VideoChatScheduled(context, target=chat, start_date=raw_event.message.video_chat_scheduled.start_date)

    @m.entity(TelegramCapability.event_callback, event_type="event.video_chat_participants_invited")
    async def video_chat_participants_invited(self, event_type: str, raw_event: Update):
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
        users = [
            Selector().land(account.route["land"]).id(user.id).user(user.username)
            for user in raw_event.message.video_chat_participants_invited.users
        ]

        return VideoChatParticipantsInvited(context, target=chat, users=users)
