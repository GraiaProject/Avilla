from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.selector import Selector
from avilla.core.trait.context import bounds, pull
from avilla.spec.core.profile.metadata import Nick, Summary

if TYPE_CHECKING:
    from avilla.core.context import Context


with bounds("account"):

    @pull(Summary)
    async def get_account_summary(cx: Context, target: Selector):
        result = await cx.account.call(
            "userProfile",
            {
                "__method__": "fetch",
                "target": int(target.pattern["account"]),
            },
        )
        return Summary(result["nickname"], "a account stranger on platform qq")

    @pull(Nick)
    async def get_friend_nick(cx: Context, target: Selector):
        result = await cx.account.call(
            "userProfile",
            {
                "__method__": "fetch",
                "target": int(target.pattern["account"]),
            },
        )
        return Nick(result["nickname"], result["nickname"], None)
