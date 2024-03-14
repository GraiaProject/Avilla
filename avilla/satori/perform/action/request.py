from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.request import RequestCapability

if TYPE_CHECKING:
    from avilla.satori.account import SatoriAccount  # noqa
    from avilla.satori.protocol import SatoriProtocol  # noqa


class SatoriRequestActionPerform((m := AccountCollector["SatoriProtocol", "SatoriAccount"]())._):
    m.namespace = "avilla.protocol/satori::action"
    m.identify = "request"

    @m.entity(RequestCapability.accept, target="land.guild.member.request")
    async def accept_member_join_request(self, target: Selector) -> None:
        request_id = target.pattern["request"]
        await self.account.client.guild_approve(
            request_id=request_id,
            approve=True,
            comment="",
        )

    @m.entity(RequestCapability.reject, target="land.guild.member.request")
    async def reject_member_join_request(self, target: Selector, reason: str | None = None, forever: bool = False) -> None:
        request_id = target.pattern["request"]
        await self.account.client.guild_approve(
            request_id=request_id,
            approve=False,
            comment=reason or "",
        )

    @m.entity(RequestCapability.accept, target="land.user.request")
    async def accept_new_friend_request(self, target: Selector) -> None:
        request_id = target.pattern["request"]
        await self.account.client.friend_approve(
            request_id=request_id,
            approve=True,
            comment="",
        )

    @m.entity(RequestCapability.reject, target="land.user.request")
    async def reject_new_friend_request(self, target: Selector, reason: str | None = None, forever: bool = False) -> None:
        request_id = target.pattern["request"]
        await self.account.client.friend_approve(
            request_id=request_id,
            approve=False,
            comment=reason or "",
        )

    @m.entity(RequestCapability.accept, target="land.guild.request")
    async def accept_bot_invited_request(self, target: Selector) -> None:
        request_id = target.pattern["request"]
        await self.account.client.guild_approve(
            request_id=request_id,
            approve=True,
            comment="",
        )

    @m.entity(RequestCapability.reject, target="land.guild.request")
    async def reject_bot_invited_request(
        self, target: Selector, reason: str | None = None, forever: bool = False
    ) -> None:
        request_id = target.pattern["request"]
        await self.account.client.guild_approve(
            request_id=request_id,
            approve=False,
            comment=reason or "",
        )
