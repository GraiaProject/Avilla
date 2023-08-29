from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.exceptions import permission_error_message
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.qqguild.tencent.const import PRIVILEGE_TRANS
from avilla.standard.core.privilege import MuteAllCapability, Privilege
from avilla.standard.core.profile import Summary, SummaryCapability

if TYPE_CHECKING:
    from avilla.qqguild.tencent.account import QQGuildAccount  # noqa
    from avilla.qqguild.tencent.protocol import QQGuildProtocol  # noqa


class QQGuildChannelActionPerform((m := AccountCollector["QQGuildProtocol", "QQGuildAccount"]())._):
    m.post_applying = True

    @m.pull("land.guild.channel", Summary)
    async def get_summary(self, target: Selector) -> Summary:
        result = await self.account.connection.call("get", f"channels/{target.pattern['channel']}", {})
        return Summary(result["name"], None)

    @m.pull("land.guild.channel", Privilege)
    async def get_privilege(self, target: Selector) -> Privilege:
        result = await self.account.connection.call("get", f"channels/{target.pattern['channel']}", {})
        value = int(result["permissions"]) & 1 == 1
        return Privilege(value, value)

    @m.pull("land.guild.channel", Privilege >> Summary)
    async def get_privilege_summary(self, target: Selector) -> Summary:
        result = await self.account.connection.call("get", f"channels/{target.pattern['channel']}", {})
        return Summary(PRIVILEGE_TRANS[result["permissions"]], "permission of account self")

    @SummaryCapability.set_name.collect(m, "land.guild.channel", Summary)
    async def set_name(self, target: Selector, t: ..., name: str):
        result = await self.account.connection.call("get", f"guilds/{target.pattern['guild']}/api_permission", {})
        for api in result["apis"]:
            if api["path"] == "channels/{channel_id}" and api["method"] == "PATCH":
                await self.account.connection.call("patch", f"channels/{target.pattern['channel']}", {"name": name})
                return
        raise PermissionError(permission_error_message(f"set_name@{target.path}", "read", ["manage"]))

    @MuteAllCapability.mute_all.collect(m, "land.guild.channel")
    async def channel_mute_all(self, target: Selector):
        await self.account.connection.call("patch", f"channels/{target.pattern['channel']}", {"speak_permission": 2})

    @MuteAllCapability.unmute_all.collect(m, "land.guild.channel")
    async def channel_unmute_all(self, target: Selector):
        await self.account.connection.call("patch", f"channels/{target.pattern['channel']}", {"speak_permission": 1})
