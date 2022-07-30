from __future__ import annotations
from typing import TYPE_CHECKING, Callable

from avilla.core.querier import query, ProtocolAbstractQueryHandler
from avilla.core.utilles.selector import DynamicSelector, Selector
from avilla.elizabeth.account import ElizabethAccount
from avilla.elizabeth.connection.util import CallMethod

if TYPE_CHECKING:
    from avilla.core.relationship import Relationship


class ElizabethRootQuery(ProtocolAbstractQueryHandler, prefix=Selector.any()):
    @query("group")
    async def query_group(
        self, rs: Relationship, prefix: Selector, checker: Callable[[Selector], bool]
    ):
        account = rs.avilla.get_account(selector=rs.current)
        assert isinstance(account, ElizabethAccount)
        result: list[dict] = await account.call("groupList", CallMethod.GET, {})
        for i in result:
            print(i)
            group = Selector().land(rs.land).group(str(i["id"]))
            if checker(group):
                yield group

class ElizabethGroupQuery(ProtocolAbstractQueryHandler, prefix=DynamicSelector.fragment().group("*")):
    @query("member")
    async def query_member(
        self, rs: Relationship, prefix: Selector, checker: Callable[[Selector], bool]
    ):
        account = rs.avilla.get_account(selector=rs.current)
        assert isinstance(account, ElizabethAccount)
        result: list[dict] = await account.call(
            "memberList", CallMethod.GET, {"target": int(prefix.pattern["group"])}
        )
        for i in result:
            member = Selector().land(rs.land).group(i["group"]).member(i["id"])
            if checker(member):
                yield member
