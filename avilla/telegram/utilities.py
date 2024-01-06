from functools import partial
from typing import Callable

from telegram import Update

_message_events = [
    "poll",
    "pinned_message",
    "new_chat_members",
    "left_chat_member",
    "new_chat_title",
    "new_chat_photo",
    "delete_chat_photo",
    "forum_topic_created",
    "forum_topic_edited",
    "forum_topic_closed",
    "forum_topic_reopened",
    "general_forum_topic_hidden",
    "general_forum_topic_unhidden",
    "video_chat_started",
    "video_chat_ended",
    "video_chat_scheduled",
    "video_chat_participants_invited",
]


def _message_event_type(name: str, raw: Update) -> str:
    obj: dict[str, ...] = raw.to_dict()["message"]
    for event in _message_events:
        if event in obj and obj[event] is not False:
            return f"event.{event}"

    return f"{name}.{raw.message.chat.type}"


_event_types: dict[str, Callable[[Update], str]] = {
    "message": partial(_message_event_type, "message"),
    "edited_message": lambda raw: f"edited_message.{raw.edited_message.chat.type}",
    "channel_post": partial(_message_event_type, "channel_post"),
    "edited_channel_post": lambda raw: f"edited_channel_post.{raw.edited_channel_post.chat.type}",
    "inline_query": lambda _: "inline.query",
    "chosen_inline_result": lambda _: "inline.chosen_result",
    "callback_query": lambda _: "inline.callback_query",
    "shipping_query": lambda _: "event.shipping_query",
    "pre_checkout_query": lambda _: "event.pre_checkout_query",
    "poll": lambda _: "event.poll_stop",  # Distinguish from event.poll in message
    "poll_answer": lambda _: "event.poll_answer",
    "chat_member": lambda _: "event.chat_member_updated",
    "my_chat_member": lambda _: "event.my_chat_member_updated",
    "chat_join_request": lambda _: "event.chat_join_request",
}


def reveal_event_type(raw: Update) -> str:
    update_type = list(raw.to_dict().keys())[1]
    if update_type in _event_types:
        return _event_types[update_type](raw)
    return "non-implemented"
