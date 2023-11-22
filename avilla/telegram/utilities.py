from telegram import Update


def telegram_event_type(raw: Update) -> str:
    # Dispatch Message Type
    if raw.message:
        if raw.message.chat.type == raw.message.chat.PRIVATE:
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

    # Dispatch Event Type
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
