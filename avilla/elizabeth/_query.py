from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from avilla.core.querier import ProtocolAbstractQueryHandler, query
from avilla.core.selector import Selector
from avilla.elizabeth.account import ElizabethAccount

if TYPE_CHECKING:
    from avilla.core.context import Context


class ElizabethRootQuery(ProtocolAbstractQueryHandler):
    @query("group")
    async def query_group(self, rs: Context, prefix: Selector, checker: Callable[[Selector], bool]):
        account = rs.account
        assert isinstance(account, ElizabethAccount)
        result: list[dict] = await account.call("groupList", {"__method__": "get"})
        for i in result:
            group = Selector().land(rs.land).group(str(i["id"]))
            if checker(group):
                yield group


class ElizabethGroupQuery(ProtocolAbstractQueryHandler, prefix="group"):
    @query("member")
    async def query_member(self, rs: Context, prefix: Selector, checker: Callable[[Selector], bool]):
        account = rs.account
        assert isinstance(account, ElizabethAccount)
        result: list[dict] = await account.call(
            "memberList", {"__method__": "get", "target": int(prefix.pattern["group"])}
        )
        for i in result:
            member = Selector().land(rs.land).group(str(i["group"]["id"])).member(str(i["id"]))
            if checker(member):
                yield member
