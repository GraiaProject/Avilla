from __future__ import annotations

from typing import TYPE_CHECKING, Callable, cast

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from avilla.elizabeth.account import ElizabethAccount  # noqa
    from avilla.elizabeth.protocol import ElizabethProtocol  # noqa


class ElizabethBotQueryPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.namespace = "avilla.protocol/elizabeth::query"
    m.identify = "bot"

    @CoreCapability.query.collect(m, "land.account")
    async def query_account(self, predicate: Callable[[str, str], bool] | str, previous: None):
        result = await self.account.connection.call("fetch", "botList", {}, session=False)
        result = cast(list, result)
        for i in result:
            account_id = str(i)
            if callable(predicate) and predicate("account", account_id) or account_id == predicate:
                yield Selector().land(self.account.route["land"]).account(account_id)
