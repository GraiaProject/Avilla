from telegram import Update


def telegram_event_type(raw: Update) -> str:
    if raw.message:
        if raw.message.chat.type == raw.message.chat.PRIVATE:
            return "message.private"
        elif raw.message.chat.type == raw.message.chat.GROUP:
            return "message.group"
