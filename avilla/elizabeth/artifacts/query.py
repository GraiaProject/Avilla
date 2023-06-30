from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.selector import Selector
from avilla.core.trait.context import query

if TYPE_CHECKING:
    from avilla.core.context import Context


@query("group")
async def get_groups(cx: Context, upper: None, predicate: Selector):
    print(111, cx.account)
    result: list[dict] = await cx.account.call("groupList", {"__method__": "fetch"})
    print(result)
    for i in result:
        group = Selector().group(str(i["id"]))
        if predicate.matches(group):
            yield group


@query("group", "member")
async def get_group_members(cx: Context, upper: Selector, predicate: Selector):
    print(4)
    result: list[dict] = await cx.account.call(
        "memberList", {"__method__": "fetch", "target": int(upper.pattern["group"])}
    )
    for i in result:
        member = Selector().group(str(i["group"]["id"])).member(str(i["id"]))
        if predicate.matches(member):
            yield member