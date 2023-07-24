from __future__ import annotations

from typing import TYPE_CHECKING, cast

from avilla.core.exceptions import UnknownTarget
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.common import Count
from avilla.standard.core.privilege import MuteAllCapability
from avilla.standard.core.profile import Nick, Summary
from avilla.standard.core.relation import SceneCapability

if TYPE_CHECKING:
    from avilla.red.account import RedAccount  # noqa
    from avilla.red.protocol import RedProtocol  # noqa


class RedGroupActionPerform((m := AccountCollector["RedProtocol", "RedAccount"]())._):
    m.post_applying = True

    @m.pull("land.group", Summary)
    async def get_summary(self, target: Selector) -> Summary:
        result = await self.account.websocket_client.call_http("get", "api/bot/groups", {})
        result = cast(list, result)
        for i in result:
            group_id = str(i["groupCode"])
            if group_id == target["group"]:
                return Summary(i["groupName"], "name of group")
        raise UnknownTarget("Group not found")

    @m.pull("land.group", Nick)
    async def get_nick(self, target: Selector) -> Nick:
        result = await self.account.websocket_client.call_http("get", "api/bot/groups", {})
        result = cast(list, result)
        for i in result:
            group_id = str(i["groupCode"])
            if group_id == target["group"]:
                return Nick(i["groupName"], i["remarkName"], None)
        raise UnknownTarget("Group not found")

    @m.pull("land.group", Count)
    async def get_count(self, target: Selector) -> Count:
        result = await self.account.websocket_client.call_http("get", "api/bot/groups", {})
        result = cast(list, result)
        for i in result:
            group_id = str(i["groupCode"])
            if group_id == target["group"]:
                return Count(i["memberCount"], i["maxMember"])
        raise UnknownTarget("Group not found")

    @MuteAllCapability.mute_all.collect(m, "land.group")
    async def mute_all(self, target: Selector):
        await self.account.websocket_client.call_http(
            "post", "api/group/muteEveryone", {"group": int(target["group"]), "enable": True}
        )

    @MuteAllCapability.unmute_all.collect(m, "land.group")
    async def unmute_all(self, target: Selector):
        await self.account.websocket_client.call_http(
            "post", "api/group/muteEveryone", {"group": int(target["group"]), "enable": False}
        )

    @SceneCapability.remove_member.collect(m, "land.group.member")
    async def remove_member(self, target: Selector, reason: str | None = None):
        await self.account.websocket_client.call_http(
            "post",
            "api/group/kick",
            {
                "group": int(target["group"]),
                "uidList": [int(target["member"])],
                "reason": reason or "",
                "refuseForever": False,
            },
        )
