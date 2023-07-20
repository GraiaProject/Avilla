from __future__ import annotations

from typing import TYPE_CHECKING, Callable, cast

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from ...account import ElizabethAccount  # noqa
    from ...protocol import ElizabethProtocol  # noqa


class ElizabethAnnouncementQueryPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.post_applying = True

    @CoreCapability.query.collect(m, "announcement", "land.group")
    async def query_group_announcement(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        result = await self.account.connection.call(
            "fetch", "anno_list", {"id": int(previous["group"]), "offset": 0, "size": 10}
        )
        result = cast(list, result)
        for i in result:
            announce_id = str(i["fid"])
            if callable(predicate) and predicate("announcement", announce_id) or announce_id == predicate:
                yield Selector().land(self.account.route["land"]).group(previous["group"]).announcement(announce_id)
