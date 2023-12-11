from functools import partial
from typing import Callable

from telegram import Update

_sub_event = [
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
]


def _message_dispatcher(name: str, raw: Update) -> str:
    obj: dict[str, ...] = raw.to_dict()["message"]
    for sub in _sub_event:
        if sub in obj and obj[sub] is not False:
            return f"event.{sub}"

    return f"{name}.{raw.message.chat.type}"


_dispatchers: dict[str, Callable[[Update], str]] = {
    "message": partial(_message_dispatcher, "message"),
    "edited_message": lambda raw: f"edited_message.{raw.edited_message.chat.type}",
    "channel_post": partial(_message_dispatcher, "channel_post"),
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


def telegram_event_type(raw: Update) -> str:
    update_type = list(raw.to_dict().keys())[1]
    if update_type in _dispatchers:
        return _dispatchers[update_type](raw)
    return "non-implemented"
