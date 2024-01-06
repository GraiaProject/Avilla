from __future__ import annotations

from telegram import Update

from avilla.core.context import Context
from avilla.core.selector import Selector
from avilla.standard.telegram.event import (
    VideoChatEnded,
    VideoChatParticipantsInvited,
    VideoChatScheduled,
    VideoChatStarted,
)
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.collector.instance import InstanceCollector


class TelegramEventVideoChatPerform((m := InstanceCollector())._):
    m.namespace = "avilla.protocol/telegram::event"
    m.identify = "video_chat"

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
