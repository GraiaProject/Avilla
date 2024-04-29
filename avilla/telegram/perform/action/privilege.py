from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from avilla.core import Selector
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.standard.core.privilege import BanCapability, MuteCapability

if TYPE_CHECKING:
    from avilla.telegram.account import TelegramAccount  # noqa
    from avilla.telegram.protocol import TelegramProtocol  # noqa


class TelegramPrivilegeActionPerform((m := AccountCollector["TelegramProtocol", "TelegramAccount"]())._):
    m.namespace = "avilla.protocol/telegram::action"
    m.identify = "privilege"

    @m.entity(BanCapability.ban, target="land.chat.member")
    @m.entity(BanCapability.ban, target="land.chat.thread.member")
    async def ban_member(
        self, target: Selector, *, duration: timedelta | None = None, reason: str | None = None
    ) -> None:
        until_date = int((datetime.now() + duration).timestamp()) if duration else None
        await self.account.connection.call(
            "banChatMember",
            chat_id=target.into("::chat").last_value,
            user_id=target.last_value,
            until_date=until_date,
        )

    @m.entity(BanCapability.unban, target="land.chat.member")
    @m.entity(BanCapability.unban, target="land.chat.thread.member")
    async def unban_member(self, target: Selector) -> None:
        await self.account.connection.call(
            "unbanChatMember", chat_id=target.into("::chat").last_value, user_id=target.last_value
        )

    @m.entity(MuteCapability.mute, target="land.chat.member")
    @m.entity(MuteCapability.mute, target="land.chat.thread.member")
    async def mute_member(self, target: Selector, duration: timedelta) -> None:
        until_date = int((datetime.now() + duration).timestamp())
        await self.account.connection.call(
            "restrictChatMember",
            chat_id=target.into("::chat").last_value,
            user_id=target.last_value,
            permissions={
                "can_send_messages": False,
                "can_send_audios": False,
                "can_send_documents": False,
                "can_send_photos": False,
                "can_send_videos": False,
                "can_send_video_notes": False,
                "can_send_voice_notes": False,
                "can_send_polls": False,
                "can_send_other_messages": False,
                "can_add_web_page_previews": False,
            },
            until_date=until_date,
        )

    @m.entity(MuteCapability.unmute, target="land.chat.member")
    @m.entity(MuteCapability.unmute, target="land.chat.thread.member")
    async def unmute_member(self, target: Selector) -> None:
        await self.account.connection.call(
            "restrictChatMember",
            chat_id=target.into("::chat").last_value,
            user_id=target.last_value,
            permissions={
                "can_send_messages": True,
                "can_send_audios": True,
                "can_send_documents": True,
                "can_send_photos": True,
                "can_send_videos": True,
                "can_send_video_notes": True,
                "can_send_voice_notes": True,
                "can_send_polls": True,
                "can_send_other_messages": True,
                "can_add_web_page_previews": True,
            },
        )
