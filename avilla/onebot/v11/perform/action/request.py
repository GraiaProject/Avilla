from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.request import RequestCapability

if TYPE_CHECKING:
    from ...account import OneBot11Account  # noqa
    from ...protocol import OneBot11Protocol  # noqa


class Onebot11RequestActionPerform((m := AccountCollector["OneBot11Protocol", "OneBot11Account"]())._):
    m.namespace = "avilla.protocol/onebot11::action"
    m.identify = "request"

    @m.entity(RequestCapability.accept, target="land.user.request")
    async def accept_contact_request(self, target: Selector) -> None:
        await self.account.connection.call(
            "set_friend_add_request",
            {
                "flag": target.pattern["request"].split("@")[-1],
                "approve": True,
            },
        )

    @m.entity(RequestCapability.reject, target="land.user.request")
    async def reject_contact_request(self, target: Selector, reason: str | None = None, forever: bool = False) -> None:
        await self.account.connection.call(
            "set_friend_add_request",
            {
                "flag": target.pattern["request"].split("@")[-1],
                "approve": False,
            },
        )

    @m.entity(RequestCapability.accept, target="land.group.request")
    async def accept_bot_invited_request(self, target: Selector) -> None:
        sub_type, flag = target.pattern["request"].split("@")[-1].split("_", 1)
        await self.account.connection.call(
            "set_group_add_request",
            {
                "flag": flag,
                "sub_type": sub_type,
                "approve": True,
            },
        )

    @m.entity(RequestCapability.reject, target="land.group.request")
    async def reject_bot_invited_request(
        self, target: Selector, reason: str | None = None, forever: bool = False
    ) -> None:
        sub_type, flag = target.pattern["request"].split("@")[-1].split("_", 1)
        await self.account.connection.call(
            "set_group_add_request",
            {
                "flag": flag,
                "sub_type": sub_type,
                "approve": False,
                "reason": reason or "",
            },
        )
