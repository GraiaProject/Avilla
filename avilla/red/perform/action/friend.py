from __future__ import annotations

from typing import TYPE_CHECKING, cast

from avilla.core.exceptions import UnknownTarget
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.profile import Nick, Summary

if TYPE_CHECKING:
    from avilla.red.account import RedAccount  # noqa
    from avilla.red.protocol import RedProtocol  # noqa


class RedFriendActionPerform((m := AccountCollector["RedProtocol", "RedAccount"]())._):
    m.post_applying = True

    @m.pull("land.friend", Summary)
    async def get_summary(self, target: Selector) -> Summary:
        result = await self.account.websocket_client.call_http("get", "api/bot/friends", {})
        result = cast(list, result)
        for i in result:
            friend_id = str(i["uin"])
            if friend_id == target["friend"]:
                return Summary(i["nick"], "name of friend")
        raise UnknownTarget("Friend not found")

    @m.pull("land.friend", Nick)
    async def get_nick(self, target: Selector) -> Nick:
        result = await self.account.websocket_client.call_http("get", "api/bot/friends", {})
        result = cast(list, result)
        for i in result:
            friend_id = str(i["uin"])
            if friend_id == target["friend"]:
                return Nick(i["nick"], i["remark"], i["longNick"])
        raise UnknownTarget("Friend not found")
