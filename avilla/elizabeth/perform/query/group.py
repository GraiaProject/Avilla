from __future__ import annotations

from typing import TYPE_CHECKING, Callable, cast

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from ...account import ElizabethAccount  # noqa
    from ...protocol import ElizabethProtocol  # noqa


class ElizabethGroupQueryPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.post_applying = True

    @CoreCapability.query.collect(m, "land.group")
    async def query_group(self, predicate: Callable[[str, str], bool] | str, previous: None):
        result = await self.account.connection.call("fetch", "groupList", {})
        result = cast(list, result)
        for i in result:
            group_id = str(i["id"])
            if callable(predicate) and predicate("group", group_id) or group_id == predicate:
                yield Selector().land(self.account.route["land"]).group(group_id)

    @CoreCapability.query.collect(m, "member", "land.group")
    async def query_group_members(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        result = await self.account.connection.call("fetch", "memberList", {"target": int(previous["group"])})
        if isinstance(predicate, str) and predicate == str(self.account.route["account"]):
            yield previous.member(predicate)  # bot self not in memberList
            return
        result = cast(list, result)
        for i in result:
            member_id = str(i["id"])
            if callable(predicate) and predicate("member", member_id) or member_id == predicate:
                yield previous.member(member_id)
