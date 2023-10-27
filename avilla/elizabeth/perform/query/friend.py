from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Callable, cast

from graia.amnesia.builtins.memcache import MemcacheService

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from avilla.elizabeth.account import ElizabethAccount  # noqa
    from avilla.elizabeth.protocol import ElizabethProtocol  # noqa


class ElizabethFriendQueryPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.namespace = "avilla.protocol/elizabeth::query"
    m.identify = "friend"

    @CoreCapability.query.collect(m, "land.friend")
    async def query_friend(self, predicate: Callable[[str, str], bool] | str, previous: None):
        cache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        result = await self.account.connection.call("fetch", "friendList", {})
        result = cast(list, result)
        for i in result:
            friend_id = str(i["id"])
            await cache.set(
                f"elizabeth/account({self.account.route['account']}).friend({friend_id})", i, timedelta(minutes=5)
            )
            if callable(predicate) and predicate("friend", friend_id) or friend_id == predicate:
                yield Selector().land(self.account.route["land"]).friend(friend_id)
