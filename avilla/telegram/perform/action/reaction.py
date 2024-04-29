from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core import Selector
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.standard.telegram.reaction.capability import ReactionCapability

if TYPE_CHECKING:
    from avilla.telegram.account import TelegramAccount  # noqa
    from avilla.telegram.protocol import TelegramProtocol  # noqa


class TelegramReactionActionPerform((m := AccountCollector["TelegramProtocol", "TelegramAccount"]())._):
    m.namespace = "avilla.protocol/telegram::action"
    m.identify = "reaction"

    @m.entity(ReactionCapability.set, target="land.chat.message")
    @m.entity(ReactionCapability.set, target="land.chat.thread.message")
    async def set_message_reaction(self, target: Selector, emoji: list[str], is_big: bool | None = None) -> None:
        # <editor-fold desc="Accepted Emojis (Non-Premium)">
        non_premium_emoji = [
            "👍",
            "👎",
            "❤",
            "🔥",
            "🥰",
            "👏",
            "😁",
            "🤔",
            "🤯",
            "😱",
            "🤬",
            "😢",
            "🎉",
            "🤩",
            "🤮",
            "💩",
            "🙏",
            "👌",
            "🕊",
            "🤡",
            "🥱",
            "🥴",
            "😍",
            "🐳",
            "❤‍🔥",
            "🌚",
            "🌭",
            "💯",
            "🤣",
            "⚡",
            "🍌",
            "🏆",
            "💔",
            "🤨",
            "😐",
            "🍓",
            "🍾",
            "💋",
            "🖕",
            "😈",
            "😴",
            "😭",
            "🤓",
            "👻",
            "👨‍💻",
            "👀",
            "🎃",
            "🙈",
            "😇",
            "😨",
            "🤝",
            "✍",
            "🤗",
            "🫡",
            "🎅",
            "🎄",
            "☃",
            "💅",
            "🤪",
            "🗿",
            "🆒",
            "💘",
            "🙉",
            "🦄",
            "😘",
            "💊",
            "🙊",
            "😎",
            "👾",
            "🤷‍♂",
            "🤷",
            "🤷‍♀",
            "😡",
        ]
        # </editor-fold>
        reaction = []
        for _emoji in emoji:
            if _emoji in non_premium_emoji:
                reaction.append({"type": "emoji", "emoji": _emoji})
            else:
                reaction.append({"type": "custom_emoji", "custom_emoji_id": _emoji})

        await self.account.connection.call(
            "setMessageReaction",
            chat_id=target.into("::chat").last_value,
            message_id=target.last_value,
            reaction=reaction,
            is_big=is_big,
        )
