from __future__ import annotations

from typing import TYPE_CHECKING, Callable, cast

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from avilla.onebot.v11.account import OneBot11Account  # noqa
    from avilla.onebot.v11.protocol import OneBot11Protocol  # noqa


class OneBot11GroupQueryPerform((m := AccountCollector["OneBot11Protocol", "OneBot11Account"]())._):
    m.namespace = "avilla.protocol/onebot11::query"
    m.identify = "group"

    @CoreCapability.query.collect(m, "land.group")
    async def query_group(self, predicate: Callable[[str, str], bool] | str, previous: None):
        result = await self.account.connection.call("get_group_list", {})
        result = cast(list, result)
        for i in result:
            group_id = str(i["group_id"])
            if callable(predicate) and predicate("group", group_id) or group_id == predicate:
                yield Selector().land(self.account.route["land"]).group(group_id)

    @CoreCapability.query.collect(m, "member", "land.group")
    async def query_group_members(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        result = await self.account.connection.call("get_group_member_list", {"group_id": int(previous["group"])})
        result = cast(list, result)
        for i in result:
            member_id = str(i["user_id"])
            if callable(predicate) and predicate("member", member_id) or member_id == predicate:
                yield previous.member(member_id)
