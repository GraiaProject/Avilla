from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.exceptions import permission_error_message
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.profile import Nick, Summary
from avilla.standard.core.privilege import Privilege, PrivilegeCapability
from avilla.qqguild.tencent.const import PRIVILEGE_TRANS

if TYPE_CHECKING:
    from avilla.qqguild.tencent.account import QQGuildAccount  # noqa
    from avilla.qqguild.tencent.protocol import QQGuildProtocol  # noqa


class QQGuildMemberActionPerform((m := AccountCollector["QQGuildProtocol", "QQGuildAccount"]())._):
    m.post_applying = True

    @m.pull("land.guild.user", Nick)
    async def get_summary(self, target: Selector) -> Nick:
        result = await self.account.connection.call(
            "get",
            f"guilds/{target.pattern['guild']}/members/{target.pattern['user']}",
            {}
        )
        return Nick(result["user"]["useranme"], result["nickname"], None)

    @m.pull("land.guild.channel.member", Privilege)
    async def get_privilege(self, target: Selector) -> Privilege:
        apis = await self.account.connection.call("get", f"guilds/{target.pattern['guild']}/api_permissions", {})
        for api in apis["apis"]:
            if api["path"] == "/channels/{channel_id}/members/{user_id}/permissions" and api["method"] == "GET":
                result = await self.account.connection.call(
                    "get",
                    f"channels/{target.pattern['channel']}/members/{target.pattern['member']}/permissions",
                    {}
                )
                value = int(result["permissions"]) & 2 == 2
                return Privilege(value, value)
        raise permission_error_message(
            f"get_permission@{target.path}", "read", ["manage"]
        )