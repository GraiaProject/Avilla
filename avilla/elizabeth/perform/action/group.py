from __future__ import annotations

from typing import TYPE_CHECKING, Callable, cast

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.context import ContextCollector
from avilla.core.selector import Selector
from avilla.standard.core.profile import Summary

if TYPE_CHECKING:
    from ...account import ElizabethAccount  # noqa
    from ...protocol import ElizabethProtocol  # noqa


class ElizabethGroupActionPerform((m := ContextCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.post_applying = True

    @m.pull("lang.group", Summary)
    async def get_summary(self, target: Selector) -> Summary:
        result = await self.account.connection.call(
            "fetch",
            "groupConfig",
            {
                "target": int(target.pattern["group"]),
            },
        )
        assert result is not None
        return Summary(result["name"], None)

    @CoreCapability.query.collect(m, "group")
    async def query_group(self, predicate: Callable[[str, str], bool] | str, previous: Selector | None = None):
        result = await self.account.connection.call("fetch", "groupList", {})
        result = cast(list, result)
        for i in result:
            yield Selector().land(self.account.route["land"]).group(str(i["id"]))
            # TODO:
