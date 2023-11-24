from telegram import Update


def telegram_event_type(raw: Update) -> str:
    # Dispatch Message Type
    if raw.message:
        # Dispatch Message (Service) Event Type
        if raw.message.new_chat_members:
            return "event.new_chat_members"
        elif raw.message.left_chat_member:
            return "event.left_chat_member"
        elif raw.message.new_chat_title:
            return "event.new_chat_title"
        elif raw.message.new_chat_photo:
            return "event.new_chat_photo"
        elif raw.message.delete_chat_photo:
            return "event.delete_chat_photo"
        elif raw.message.group_chat_created:
            return "event.group_chat_created"
        elif raw.message.supergroup_chat_created:
            return "event.supergroup_chat_created"
        elif raw.message.channel_chat_created:
            return "event.channel_chat_created"
        elif raw.message.migrate_to_chat_id:
            return "event.migrate_to_chat_id"
        elif raw.message.migrate_from_chat_id:
            return "event.migrate_from_chat_id"
        elif raw.message.pinned_message:
            return "event.pinned_message"
        elif raw.message.proximity_alert_triggered:
            return "event.proximity_alert_triggered"
        elif raw.message.video_chat_started:
            return "event.video_chat_started"
        elif raw.message.video_chat_ended:
            return "event.video_chat_ended"
        elif raw.message.video_chat_participants_invited:
            return "event.video_chat_participants_invited"
        elif raw.message.message_auto_delete_timer_changed:
            return "event.message_auto_delete_timer_changed"
        elif raw.message.forum_topic_created:
            return "event.forum_topic_created"
        elif raw.message.forum_topic_closed:
            return "event.forum_topic_closed"
        elif raw.message.forum_topic_reopened:
            return "event.forum_topic_reopened"
        elif raw.message.forum_topic_edited:
            return "event.forum_topic_edited"
        elif raw.message.general_forum_topic_hidden:
            return "event.general_forum_topic_hidden"
        elif raw.message.general_forum_topic_unhidden:
            return "event.general_forum_topic_unhidden"
        elif raw.message.write_access_allowed:
            return "event.write_access_allowed"

        # Dispatch Message-only Event Type
        elif raw.message.chat.type == raw.message.chat.PRIVATE:
            return "message.private"
        elif raw.message.chat.type == raw.message.chat.GROUP:
            return "message.group"
        elif raw.message.chat.type == raw.message.chat.SUPERGROUP:
            return "message.super_group"
        elif raw.message.chat.type == raw.message.chat.CHANNEL:
            return "message.channel"

    # Dispatch Edited Message Type
    elif raw.edited_message:
        if raw.edited_message.chat.type == raw.edited_message.chat.PRIVATE:
            return "edited_message.private"
        elif raw.edited_message.chat.type == raw.edited_message.chat.GROUP:
            return "edited_message.group"
        elif raw.edited_message.chat.type == raw.edited_message.chat.SUPERGROUP:
            return "edited_message.super_group"
        elif raw.edited_message.chat.type == raw.edited_message.chat.CHANNEL:
            return "edited_message.channel"

    # Dispatch Callback Type
    elif raw.callback_query:
        if raw.callback_query.message.chat.type == raw.callback_query.message.chat.PRIVATE:
            return "callback.private"
        elif raw.callback_query.message.chat.type == raw.callback_query.message.chat.GROUP:
            return "callback.group"
        elif raw.callback_query.message.chat.type == raw.callback_query.message.chat.SUPERGROUP:
            return "callback.super_group"
        elif raw.callback_query.message.chat.type == raw.callback_query.message.chat.CHANNEL:
            return "callback.channel"

    # Dispatch Inline Type
    elif raw.inline_query:
        # TODO: Implement inline query for all chat types
        return "inline.query"
    elif raw.chosen_inline_result:
        return "inline.result"

    # Dispatch Non-message Event Type
    elif raw.poll:
        return "event.poll"
    elif raw.poll_answer:
        return "event.poll_answer"
    elif raw.my_chat_member:
        return "event.my_chat_member"
    elif raw.chat_member:
        return "event.chat_member"
    elif raw.chat_join_request:
        return "event.chat_join_request"

    # Not implemented yet since Invoice is not implemented
    # elif raw.pre_checkout_query:
    #     return "pre_checkout_query"
    # elif raw.shipping_query:
    #     return "shipping_query"

    return "non-implemented"
