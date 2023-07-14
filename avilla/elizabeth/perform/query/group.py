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

    @CoreCapability.query.collect(m, "group")
    async def query_group(self, predicate: Callable[[str, str], bool] | str, previous: Selector | None = None):
        result = await self.account.connection.call("fetch", "groupList", {})
        result = cast(list, result)
        for i in result:
            yield Selector().land(self.account.route["land"]).group(str(i["id"]))
            # TODO:
