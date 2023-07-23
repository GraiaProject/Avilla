from __future__ import annotations

from typing import TYPE_CHECKING, Callable, cast

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from ...account import ElizabethAccount  # noqa
    from ...protocol import ElizabethProtocol  # noqa


class ElizabethFriendQueryPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.post_applying = True

    @CoreCapability.query.collect(m, "land.friend")
    async def query_friend(self, predicate: Callable[[str, str], bool] | str, previous: None):
        result = await self.account.connection.call("fetch", "friendList", {})
        result = cast(list, result)
        for i in result:
            friend_id = str(i["id"])
            if callable(predicate) and predicate("friend", friend_id) or friend_id == predicate:
                yield Selector().land(self.account.route["land"]).friend(friend_id)
