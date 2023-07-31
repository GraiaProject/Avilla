from __future__ import annotations

from typing import TYPE_CHECKING, Callable, cast

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from ..account import RedAccount  # noqa
    from ..protocol import RedProtocol  # noqa


class RedQueryPerform((m := AccountCollector["RedProtocol", "RedAccount"]())._):
    m.post_applying = True

    @CoreCapability.query.collect(m, "land.group")
    async def query_group(self, predicate: Callable[[str, str], bool] | str, previous: None):
        result = await self.account.websocket_client.call_http("get", "api/bot/groups", {})
        result = cast(list, result)
        for i in result:
            group_id = str(i["groupCode"])
            if callable(predicate) and predicate("group", group_id) or group_id == predicate:
                yield Selector().land(self.account.route["land"]).group(group_id)

    @CoreCapability.query.collect(m, "land.friend")
    async def query_friend(self, predicate: Callable[[str, str], bool] | str, previous: None):
        result = await self.account.websocket_client.call_http("get", "api/bot/friends", {})
        result = cast(list, result)
        for i in result:
            friend_id = str(i["uin"])
            if callable(predicate) and predicate("friend", friend_id) or friend_id == predicate:
                yield Selector().land(self.account.route["land"]).friend(friend_id)

    @CoreCapability.query.collect(m, "member", "land.group")
    async def query_group_members(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        result = await self.account.websocket_client.call_http(
            "post", "api/group/getMemberList", {"group": int(previous["group"])}
        )
        result = cast(list, result)
        for i in result:
            member_id = str(i["qq"])
            if callable(predicate) and predicate("member", member_id) or member_id == predicate:
                yield previous.member(member_id)
