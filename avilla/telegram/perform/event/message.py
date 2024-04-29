from __future__ import annotations

from datetime import datetime
from typing import Final

from graia.amnesia.message import MessageChain

from avilla.core import (
    MemberCreated,
    MemberDestroyed,
    MetadataModified,
    SceneCreated,
    SceneDestroyed,
)
from avilla.core.context import Context
from avilla.core.event import ModifyDetail
from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageEdited, MessageReceived
from avilla.standard.core.profile import Avatar, Nick, Summary
from avilla.standard.telegram.event import (
    ProximityAlertTriggered,
    VideoChatEnded,
    VideoChatParticipantsInvited,
    VideoChatScheduled,
    VideoChatStarted,
)
from avilla.standard.telegram.message_auto_delete_timer.metadata import (
    MessageAutoDeleteTimer,
)
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.collector.connection import ConnectionCollector
from avilla.telegram.perform.action.chat import TelegramChatActionPerform

SUB_EVENTS: Final[set[str]] = {
    "new_chat_members",
    "left_chat_member",
    "new_chat_title",
    "new_chat_photo",
    "delete_chat_photo",
    "group_chat_created",  # not implemented
    "supergroup_chat_created",  # not implemented
    "channel_chat_created",  # not implemented
    "message_auto_delete_timer_changed",
    "migrate_to_chat_id",  # not implemented
    "migrate_from_chat_id",  # not implemented
    "pinned_message",  # not implemented
    "invoice",  # not implemented
    "successful_payment",  # not implemented
    "users_shared",  # not implemented
    "chat_shared",  # not implemented
    "connected_website",  # not implemented
    "write_access_allowed",  # not implemented
    "passport_data",  # not implemented
    "proximity_alert_triggered",
    "boost_added",  # not implemented
    "forum_topic_created",
    "forum_topic_edited",
    "forum_topic_closed",
    "forum_topic_reopened",
    "general_forum_topic_hidden",
    "general_forum_topic_unhidden",
    "giveaway_created",  # not implemented
    "giveaway",  # not implemented
    "giveaway_winners",  # not implemented
    "giveaway_completed",  # not implemented
    "video_chat_scheduled",
    "video_chat_started",
    "video_chat_ended",
    "video_chat_participants_invited",
    "web_app_data",  # not implemented
    "reply_markup",  # not implemented
}


class TelegramEventMessagePerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/telegram::event"
    m.identify = "message"

    @m.entity(TelegramCapability.event_callback, event_type="message")
    @m.entity(TelegramCapability.event_callback, event_type="edited_message")
    @m.entity(TelegramCapability.event_callback, event_type="channel_post")
    @m.entity(TelegramCapability.event_callback, event_type="edited_channel_post")
    async def message(self, event_type: str, raw_event: dict):
        if intersection := set(raw_event[event_type].keys()).intersection(SUB_EVENTS):
            return await TelegramCapability(self.staff).event_callback(f"{event_type}.{intersection.pop()}", raw_event)
        return await TelegramCapability(self.staff).event_callback(
            f'{event_type}.{raw_event[event_type]["chat"]["type"]}', raw_event
        )

    @m.entity(TelegramCapability.event_callback, event_type="message.private")
    @m.entity(TelegramCapability.event_callback, event_type="message.group")
    @m.entity(TelegramCapability.event_callback, event_type="message.supergroup")
    async def message_(self, event_type: str, raw_event: dict):
        account = self.account
        message: dict = raw_event["message"]
        chat = Selector().land(account.route["land"]).chat(str(message["chat"]["id"]))
        if event_type == "message.supergroup" and "message_thread_id" in message:
            chat = chat.thread(str(message["message_thread_id"]))
        context = Context(
            account,
            chat if event_type == "message.private" else chat.member(message["from"]["id"]),
            chat,
            chat,
            (account.route if event_type == "message.private" else chat.member(account.route["account"])),
        )

        # TODO: re-implement MediaGroup

        chain = await TelegramCapability(account.staff.ext({"context": context})).deserialize(message)
        reply = chat.message(message["reply_to_message"]["message_id"]) if "reply_to_message" in message else None
        return MessageReceived(
            context,
            Message(
                id=str(message["message_id"]),
                scene=chat,
                sender=chat if event_type == "message.private" else chat.member(message["from"]["id"]),
                content=chain,
                time=datetime.fromtimestamp(message["date"]),
                reply=reply,
            ),
        )

    @m.entity(TelegramCapability.event_callback, event_type="edited_message.private")
    @m.entity(TelegramCapability.event_callback, event_type="edited_message.group")
    @m.entity(TelegramCapability.event_callback, event_type="edited_message.supergroup")
    async def edited_message(self, event_type: str, raw_event: dict):
        account = self.account
        message: dict = raw_event["message"]
        chat = Selector().land(account.route["land"]).chat(str(message["chat"]["id"]))
        if event_type == "edited_message.supergroup" and "message_thread_id" in message:
            chat = chat.thread(str(message["message_thread_id"]))
        context = Context(
            account,
            chat if event_type == "edited_message.private" else chat.member(message["from"]["id"]),
            chat,
            chat,
            (account.route if event_type == "edited_message.private" else chat.member(account.route["account"])),
        )

        chain = await TelegramCapability(account.staff.ext({"context": context})).deserialize(message)
        reply = chat.message(message["reply_to_message"]["message_id"]) if "reply_to_message" in message else None
        return MessageEdited(
            context=context,
            message=Message(
                id=str(message["message_id"]),
                scene=chat,
                sender=chat if event_type == "edited_message.private" else chat.member(message["from"]["id"]),
                content=chain,
                time=datetime.fromtimestamp(message["date"]),
                reply=reply,
            ),
            operator=chat if event_type == "edited_message.private" else chat.member(message["from"]["id"]),
            past=MessageChain([]),
            current=chain,
        )

    @m.entity(TelegramCapability.event_callback, event_type="message.new_chat_members")
    async def new_chat_members(self, event_type: str, raw_event: dict):
        account = self.account
        for user in raw_event["message"]["new_chat_members"]:
            chat = Selector().land(self.account.route["land"]).chat(str(raw_event["message"]["chat"]["id"]))
            member = chat.member(str(user["id"]))
            context = Context(account, member, chat, chat, chat.member(account.route["account"]))
            context._collect_metadatas(
                member,
                Nick(username := TelegramChatActionPerform.extract_username(user), username, user.get("title")),
                Summary(username, None),
            )
            context._collect_metadatas(
                chat,
                Nick(chat_name := raw_event["message"]["chat"]["title"], chat_name, None),
                Summary(chat_name, None),
            )
            if member.last_value == account.route["account"]:
                event = SceneCreated(context)
            else:
                event = MemberCreated(context)

            account.avilla.event_record(event)
            account.avilla.broadcast.postEvent(event)

    @m.entity(TelegramCapability.event_callback, event_type="message.left_chat_member")
    async def left_chat_member(self, event_type: str, raw_event: dict):
        account = self.account
        user = raw_event["message"]["left_chat_member"]
        chat = Selector().land(self.account.route["land"]).chat(str(raw_event["message"]["chat"]["id"]))
        member = chat.member(str(user["id"]))
        context = Context(account, member, chat, chat, chat.member(account.route["account"]))
        context._collect_metadatas(
            member,
            Nick(username := TelegramChatActionPerform.extract_username(user), username, user.get("title")),
            Summary(username, None),
        )
        context._collect_metadatas(
            chat,
            Nick(chat_name := raw_event["message"]["chat"]["title"], chat_name, None),
            Summary(chat_name, None),
        )

        return (
            SceneDestroyed(context, active=False)
            if member.last_value == account.route["account"]
            else MemberDestroyed(context, active=True)
        )

    @m.entity(TelegramCapability.event_callback, event_type="message.new_chat_title")
    async def new_chat_title(self, event_type: str, raw_event: dict):
        chat = Selector().land(self.account.route["land"]).chat(str(raw_event["message"]["chat"]["id"]))
        context = Context(self.account, chat, chat, chat, chat.member(self.account.route["account"]))
        context._collect_metadatas(
            chat,
            Nick(chat_name := raw_event["message"]["chat"]["title"], chat_name, None),
            Summary(chat_name, None),
        )
        return MetadataModified(
            context, chat, Summary, {Summary.inh().name: ModifyDetail("update", current=chat_name)}, scene=chat
        )

    @m.entity(TelegramCapability.event_callback, event_type="message.new_chat_photo")
    async def new_chat_photo(self, event_type: str, raw_event: dict):
        chat = Selector().land(self.account.route["land"]).chat(str(raw_event["message"]["chat"]["id"]))
        context = Context(self.account, chat, chat, chat, chat.member(self.account.route["account"]))
        return MetadataModified(context, chat, Avatar, {Avatar.inh().url: ModifyDetail("update")}, scene=chat)

    @m.entity(TelegramCapability.event_callback, event_type="message.delete_chat_photo")
    async def delete_chat_photo(self, event_type: str, raw_event: dict):
        chat = Selector().land(self.account.route["land"]).chat(str(raw_event["message"]["chat"]["id"]))
        context = Context(self.account, chat, chat, chat, chat.member(self.account.route["account"]))
        return MetadataModified(context, chat, Avatar, {Avatar.inh().url: ModifyDetail("clear")}, scene=chat)

    @m.entity(TelegramCapability.event_callback, event_type="message.message_auto_delete_timer_changed")
    async def message_auto_delete_timer_changed(self, event_type: str, raw_event: dict):
        chat = Selector().land(self.account.route["land"]).chat(str(raw_event["message"]["chat"]["id"]))
        context = Context(self.account, chat, chat, chat, chat.member(self.account.route["account"]))
        return MetadataModified(
            context,
            chat,
            MessageAutoDeleteTimer,
            {
                MessageAutoDeleteTimer.inh().message_auto_delete_time: ModifyDetail(
                    "update",
                    current=raw_event["message"]["message_auto_delete_timer_changed"]["message_auto_delete_time"],
                )
            },
            scene=chat,
        )

    @m.entity(TelegramCapability.event_callback, event_type="message.proximity_alert_triggered")
    async def proximity_alert_triggered(self, event_type: str, raw_event: dict):
        chat = Selector().land(self.account.route["land"]).chat(str(raw_event["message"]["chat"]["id"]))
        context = Context(self.account, chat, chat, chat, chat.member(self.account.route["account"]))
        return ProximityAlertTriggered(
            context,
            Selector().land(self.account.route["land"]).member(str(raw_event["message"]["traveler"]["id"])),
            Selector().land(self.account.route["land"]).member(str(raw_event["message"]["watcher"]["id"])),
            raw_event["message"]["distance"],
        )

    @m.entity(TelegramCapability.event_callback, event_type="message.video_chat_scheduled")
    async def video_chat_scheduled(self, event_type: str, raw_event: dict):
        chat = Selector().land(self.account.route["land"]).chat(str(raw_event["message"]["chat"]["id"]))
        context = Context(self.account, chat, chat, chat, chat.member(self.account.route["account"]))
        return VideoChatScheduled(
            context,
            datetime.fromtimestamp(raw_event["message"]["start_date"]),
        )

    @m.entity(TelegramCapability.event_callback, event_type="message.video_chat_started")
    async def video_chat_started(self, event_type: str, raw_event: dict):
        chat = Selector().land(self.account.route["land"]).chat(str(raw_event["message"]["chat"]["id"]))
        context = Context(self.account, chat, chat, chat, chat.member(self.account.route["account"]))
        return VideoChatStarted(context)

    @m.entity(TelegramCapability.event_callback, event_type="message.video_chat_ended")
    async def video_chat_ended(self, event_type: str, raw_event: dict):
        chat = Selector().land(self.account.route["land"]).chat(str(raw_event["message"]["chat"]["id"]))
        context = Context(self.account, chat, chat, chat, chat.member(self.account.route["account"]))
        return VideoChatEnded(context, duration=raw_event["message"]["video_chat_ended"]["duration"])

    @m.entity(TelegramCapability.event_callback, event_type="message.video_chat_participants_invited")
    async def video_chat_participants_invited(self, event_type: str, raw_event: dict):
        chat = Selector().land(self.account.route["land"]).chat(str(raw_event["message"]["chat"]["id"]))
        context = Context(self.account, chat, chat, chat, chat.member(self.account.route["account"]))
        return VideoChatParticipantsInvited(
            context,
            [
                Selector().land(self.account.route["land"]).member(str(user["id"]))
                for user in raw_event["message"]["video_chat_participants_invited"]["users"]
            ],
        )
