from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Callable, cast

from graia.amnesia.builtins.memcache import MemcacheService

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from avilla.onebot.v11.account import OneBot11Account  # noqa
    from avilla.onebot.v11.protocol import OneBot11Protocol  # noqa


class ElizabethFriendQueryPerform((m := AccountCollector["OneBot11Protocol", "OneBot11Account"]())._):
    m.namespace = "avilla.protocol/onebot11::query"
    m.identify = "friend"

    @CoreCapability.query.collect(m, "land.friend")
    async def query_friend(self, predicate: Callable[[str, str], bool] | str, previous: None):
        cache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        result = await self.account.connection.call("get_friend_list", {})
        result = cast(list, result)
        for i in result:
            user_id = str(i["user_id"])
            await cache.set(
                f"onebot11/account({self.account.route['account']}).friend({user_id})", i, timedelta(minutes=5)
            )
            if callable(predicate) and predicate("friend", user_id) or user_id == predicate:
                yield Selector().land(self.account.route["land"]).friend(user_id)
