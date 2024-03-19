from __future__ import annotations

from flywheel import scoped_collect

from avilla.core.selector import Selector
from avilla.satori.bases import InstanceOfAccount
from avilla.standard.core.request import accept_request, reject_request


class SatoriRequestActionPerform(m := scoped_collect.env().target, InstanceOfAccount, static=True):

    @m.impl(accept_request, target="land.guild.member.request")
    async def accept_member_join_request(self, target: Selector) -> None:
        request_id = target.pattern["request"]
        await self.account.client.guild_approve(
            request_id=request_id,
            approve=True,
            comment="",
        )

    @m.impl(reject_request, target="land.guild.member.request")
    async def reject_member_join_request(
        self, target: Selector, reason: str | None = None, forever: bool = False
    ) -> None:
        request_id = target.pattern["request"]
        await self.account.client.guild_approve(
            request_id=request_id,
            approve=False,
            comment=reason or "",
        )

    @m.impl(accept_request, target="land.user.request")
    async def accept_new_friend_request(self, target: Selector) -> None:
        request_id = target.pattern["request"]
        await self.account.client.friend_approve(
            request_id=request_id,
            approve=True,
            comment="",
        )

    @m.impl(reject_request, target="land.user.request")
    async def reject_new_friend_request(
        self, target: Selector, reason: str | None = None, forever: bool = False
    ) -> None:
        request_id = target.pattern["request"]
        await self.account.client.friend_approve(
            request_id=request_id,
            approve=False,
            comment=reason or "",
        )

    @m.impl(accept_request, target="land.guild.request")
    async def accept_bot_invited_request(self, target: Selector) -> None:
        request_id = target.pattern["request"]
        await self.account.client.guild_approve(
            request_id=request_id,
            approve=True,
            comment="",
        )

    @m.impl(reject_request, target="land.guild.request")
    async def reject_bot_invited_request(
        self, target: Selector, reason: str | None = None, forever: bool = False
    ) -> None:
        request_id = target.pattern["request"]
        await self.account.client.guild_approve(
            request_id=request_id,
            approve=False,
            comment=reason or "",
        )
