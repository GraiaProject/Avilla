from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.selector import Selector
from avilla.core.trait.context import query

if TYPE_CHECKING:

    from avilla.core.context import Context


@query("group")
async def get_groups(ctx: Context, upper: None, predicate: Selector):
    result: list[dict] = await ctx.account.call("groupList", {"__method__": "fetch"})
    for i in result:
        group = Selector().group(str(i["id"]))
        if predicate.matches(group):
            yield group


@query("group", "member")
async def get_group_members(ctx: Context, upper: Selector, predicate: Selector):
    result: list[dict] = await ctx.account.call(
        "memberList", {"__method__": "fetch", "target": int(upper.pattern["group"])}
    )
    for i in result:
        member = Selector().group(str(i["group"]["id"])).member(str(i["id"]))
        if predicate.matches(member):
            yield member
