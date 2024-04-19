from __future__ import annotations

from datetime import datetime, timedelta
from typing import Final

from graia.amnesia.builtins.memcache import Memcache, MemcacheService
from graia.amnesia.message import MessageChain

from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageReceived
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.collector.connection import ConnectionCollector

SUB_EVENTS: Final[set[str]] = {
    "new_chat_members",
    "left_chat_member",
    "new_chat_title",
    "new_chat_photo",
    "delete_chat_photo",
    "group_chat_created",
    "supergroup_chat_created",
    "channel_chat_created",
    "message_auto_delete_timer_changed",
    "migrate_to_chat_id",
    "migrate_from_chat_id",
    "pinned_message",
    "invoice",
    "successful_payment",
    "users_shared",
    "chat_shared",
    "connected_website",
    "write_access_allowed",
    "passport_data",
    "proximity_alert_triggered",
    "boost_added",
    "forum_topic_created",
    "forum_topic_edited",
    "forum_topic_closed",
    "forum_topic_reopened",
    "general_forum_topic_hidden",
    "general_forum_topic_unhidden",
    "giveaway_created",
    "giveaway",
    "giveaway_winners",
    "giveaway_completed",
    "video_chat_scheduled",
    "video_chat_started",
    "video_chat_ended",
    "video_chat_participants_invited",
    "web_app_data",
    "reply_markup",
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
            (
                Selector().land(account.route["land"]).account(account.route["account"])
                if event_type == "message.private"
                else chat.member(account.route["account"])
            ),
        )

        # TODO: re-implement MediaGroup

        chain = await TelegramCapability(account.staff.ext({"context": context})).deserialize(message)
        reply = chat.message(message["reply_to_message"]["message_id"]) if "reply_to_message" in message else None

        cache: Memcache = self.account.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        await cache.set(
            f"telegram/chat({message['chat']['id']})",
            {
                "id": message["chat"]["id"],
                "title": message["chat"].get("title"),
                "username": message["chat"].get("username"),
                "first_name": message["chat"].get("first_name"),
                "last_name": message["chat"].get("last_name"),
            },
            expire=timedelta(minutes=5),
        )

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
