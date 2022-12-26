from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.selector import Selector
from avilla.core.trait.context import bounds, pull

from ...spec.core.profile.metadata import Nick, Summary

if TYPE_CHECKING:
    from graia.amnesia.message import __message_chain_class__

    from avilla.core.context import Context


with bounds("contact"):

    @pull(Summary)
    async def get_friend_summary(ctx: Context, target: Selector):
        result = await ctx.account.call(
            "userProfile",
            {
                "__method__": "fetch",
                "target": int(target.pattern["contact"]),
            },
        )
        return Summary(Summary, result["nickname"], "a contact on platform qq")

    @pull(Nick)
    async def get_friend_nick(ctx: Context, target: Selector):
        result = await ctx.account.call(
            "userProfile",
            {
                "__method__": "fetch",
                "target": int(target.pattern["contact"]),
            },
        )
        return Nick(Nick, result["nickname"], result["nickname"], None)
