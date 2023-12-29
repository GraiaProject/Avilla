from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.telegram.forum.capability import ForumCapability

if TYPE_CHECKING:
    from avilla.telegram.account import TelegramAccount  # noqa
    from avilla.telegram.protocol import TelegramProtocol  # noqa


class TelegramForumActionPerform((m := AccountCollector["TelegramProtocol", "TelegramAccount"]())._):
    m.namespace = "avilla.protocol/telegram::action"
    m.identify = "forum"

    @m.entity(ForumCapability.delete_topic, target="land.chat.thread")
    async def delete_topic(self, target: Selector) -> None:
        await self.account.instance.bot.delete_forum_topic(
            chat_id=target.pattern["chat"], message_thread_id=int(target.pattern["thread"])
        )

    @m.entity(ForumCapability.edit_topic, target="land.chat.thread")
    async def edit_topic(
        self,
        target: Selector,
        *,
        name: str = None,
        icon_custom_emoji_id: str = None,
    ) -> None:
        await self.account.instance.bot.edit_forum_topic(
            chat_id=target.pattern["chat"],
            message_thread_id=int(target.pattern["thread"]),
            name=name,
            icon_custom_emoji_id=icon_custom_emoji_id,
        )

    @m.entity(ForumCapability.close_topic, target="land.chat.thread")
    async def close_topic(self, target: Selector) -> None:
        await self.account.instance.bot.close_forum_topic(
            chat_id=target.pattern["chat"], message_thread_id=int(target.pattern["thread"])
        )

    @m.entity(ForumCapability.create_topic, target="land.chat")
    async def create_topic(
        self,
        target: Selector,
        name: str,
        *,
        icon_color: int = None,
        icon_custom_emoji_id: str = None,
    ) -> None:
        await self.account.instance.bot.create_forum_topic(
            chat_id=target.pattern["chat"],
            name=name,
            icon_color=icon_color,
            icon_custom_emoji_id=icon_custom_emoji_id,
        )

    @m.entity(ForumCapability.reopen_topic, target="land.chat.thread")
    async def reopen_topic(self, target: Selector) -> None:
        await self.account.instance.bot.reopen_forum_topic(
            chat_id=target.pattern["chat"], message_thread_id=int(target.pattern["thread"])
        )

    @m.entity(ForumCapability.edit_general_topic, target="land.chat")
    async def edit_general_topic(self, target: Selector, name: str) -> None:
        await self.account.instance.bot.edit_general_forum_topic(chat_id=target.pattern["chat"], name=name)

    @m.entity(ForumCapability.close_general_topic, target="land.chat")
    async def close_general_topic(self, target: Selector) -> None:
        await self.account.instance.bot.close_general_forum_topic(chat_id=target.pattern["chat"])

    @m.entity(ForumCapability.reopen_general_topic, target="land.chat")
    async def reopen_general_topic(self, target: Selector) -> None:
        await self.account.instance.bot.reopen_general_forum_topic(chat_id=target.pattern["chat"])

    @m.entity(ForumCapability.hide_general_topic, target="land.chat")
    async def hide_general_topic(self, target: Selector) -> None:
        await self.account.instance.bot.hide_general_forum_topic(chat_id=target.pattern["chat"])

    @m.entity(ForumCapability.unhide_general_topic, target="land.chat")
    async def unhide_general_topic(self, target: Selector) -> None:
        await self.account.instance.bot.unhide_general_forum_topic(chat_id=target.pattern["chat"])
