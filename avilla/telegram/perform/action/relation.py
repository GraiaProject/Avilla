from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core import Selector
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.standard.core.relation import SceneCapability

if TYPE_CHECKING:
    from avilla.telegram.account import TelegramAccount  # noqa
    from avilla.telegram.protocol import TelegramProtocol  # noqa


class TelegramRelationActionPerform((m := AccountCollector["TelegramProtocol", "TelegramAccount"]())._):
    m.namespace = "avilla.protocol/telegram::action"
    m.identify = "relation"

    @m.entity(SceneCapability.leave, target="land.chat")
    @m.entity(SceneCapability.leave, target="land.chat.thread")
    async def leave_chat(self, target: Selector) -> None:
        await self.account.connection.call("leaveChat", chat_id=target.into("::chat").last_value)

    @m.entity(SceneCapability.remove_member, target="land.chat.member")
    async def ban_member(self, target: Selector, reason: str | None = None, permanent: bool = False) -> None:
        await self.account.connection.call(
            "banChatMember",
            chat_id=target.into("::chat").last_value,
            user_id=target.last_value,
        )
