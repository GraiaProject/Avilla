from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from avilla.core.exceptions import permission_error_message
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.qqguild.tencent.const import PRIVILEGE_TRANS
from avilla.standard.core.privilege import MuteCapability, MuteInfo, Privilege
from avilla.standard.core.profile import Nick, Summary
from avilla.standard.core.relation import SceneCapability

if TYPE_CHECKING:
    from avilla.qqguild.tencent.account import QQGuildAccount  # noqa
    from avilla.qqguild.tencent.protocol import QQGuildProtocol  # noqa


class QQGuildMemberActionPerform((m := AccountCollector["QQGuildProtocol", "QQGuildAccount"]())._):
    m.post_applying = True

    @m.pull("land.guild.user", Nick)
    async def get_summary(self, target: Selector) -> Nick:
        result = await self.account.connection.call(
            "get", f"guilds/{target.pattern['guild']}/members/{target.pattern['user']}", {}
        )
        return Nick(result["user"]["useranme"], result["nickname"], None)

    @m.pull("land.guild.channel.member", Privilege)
    async def get_privilege(self, target: Selector) -> Privilege:
        self_info = await self.account.connection.call(
            "get", f"guilds/{target.pattern['guild']}/members/{self.account.route['account']}", {}
        )
        target_info = await self.account.connection.call(
            "get", f"guilds/{target.pattern['guild']}/members/{target.pattern['member']}", {}
        )
        effective = False
        if "4" in self_info["roles"]:
            effective = True
        elif "2" in self_info["roles"] and "4" not in target_info["roles"] and "2" not in target_info["roles"]:
            effective = True
        elif "5" in self_info["roles"] and target_info["roles"] == ["1"]:
            effective = True
        apis = await self.account.connection.call("get", f"guilds/{target.pattern['guild']}/api_permission", {})
        for api in apis["apis"]:
            if api["path"] == "/channels/{channel_id}/members/{user_id}/permissions" and api["method"] == "GET":
                self_permission = await self.account.connection.call(
                    "get",
                    f"channels/{target.pattern['channel']}/members/{self.account.route['account']}/permissions",
                    {},
                )
                result = await self.account.connection.call(
                    "get", f"channels/{target.pattern['channel']}/members/{target.pattern['member']}/permissions", {}
                )
                return Privilege(
                    int(result["permissions"]) & 2 == 2,
                    effective or (int(self_permission["permissions"]) & 2 == 2),
                )
        raise PermissionError(permission_error_message(f"get_permission@{target.path}", "read", ["manage"]))

    @m.pull("land.guild.channel.member", Privilege >> Summary)
    async def get_privilege_summary(self, target: Selector) -> Summary:
        apis = await self.account.connection.call("get", f"guilds/{target.pattern['guild']}/api_permission", {})
        for api in apis["apis"]:
            if api["path"] == "/channels/{channel_id}/members/{user_id}/permissions" and api["method"] == "GET":
                result = await self.account.connection.call(
                    "get", f"channels/{target.pattern['channel']}/members/{target.pattern['member']}/permissions", {}
                )
                return Summary(
                    PRIVILEGE_TRANS[int(result["permissions"])],
                    "user's permissions in channel",
                )
        raise PermissionError(permission_error_message(f"get_permission@{target.path}", "read", ["manage"]))

    @m.pull("land.guild.channel.member", MuteInfo)
    async def get_mute_info(self, target: Selector) -> MuteInfo:
        apis = await self.account.connection.call("get", f"guilds/{target.pattern['guild']}/api_permission", {})
        for api in apis["apis"]:
            if api["path"] == "/channels/{channel_id}/members/{user_id}/permissions" and api["method"] == "GET":
                result = await self.account.connection.call(
                    "get", f"channels/{target.pattern['channel']}/members/{target.pattern['member']}/permissions", {}
                )
                return MuteInfo(
                    int(result["permissions"]) & 4 == 4,
                    timedelta(seconds=0),
                )
        raise PermissionError(permission_error_message(f"get_permission@{target.path}", "read", ["manage"]))

    @MuteCapability.mute.collect(m, "land.guild.channel.member")
    async def mute(self, target: Selector, duration: timedelta) -> None:
        if not (await self.get_privilege(target)).effective:
            self_info = await self.get_privilege_summary(target.into(f"~.member{self.account.route['account']}"))
            raise PermissionError(permission_error_message(f"set_permission@{target.path}", self_info.name, ["manage"]))
        await self.account.connection.call(
            "put",
            f"channels/{target.pattern['channel']}/members/{target.pattern['member']}/permissions",
            {"add": 0, "remove": 4},
        )

    @MuteCapability.unmute.collect(m, "land.guild.channel.member")
    async def unmute(self, target: Selector) -> None:
        if not (await self.get_privilege(target)).effective:
            self_info = await self.get_privilege_summary(target.into(f"~.member{self.account.route['account']}"))
            raise PermissionError(permission_error_message(f"set_permission@{target.path}", self_info.name, ["manage"]))
        await self.account.connection.call(
            "put",
            f"channels/{target.pattern['channel']}/members/{target.pattern['member']}/permissions",
            {"add": 4, "remove": 0},
        )

    @SceneCapability.remove_member.collect(m, "land.guild.user")
    async def remove_user(self, target: Selector, reason: str | None = None) -> None:
        self_info = await self.account.connection.call(
            "get", f"guilds/{target.pattern['guild']}/members/{self.account.route['account']}", {}
        )
        effective = bool({"2", "4", "5"} & set(self_info["roles"]))
        if not effective:
            raise PermissionError(permission_error_message(f"remove_member@{target.path}", "read", ["manage"]))
        await self.account.connection.call(
            "delete", f"guilds/{target.pattern['guild']}/members/{target.pattern['user']}", {}
        )

    @SceneCapability.remove_member.collect(m, "land.guild.channel.member")
    async def remove_member(self, target: Selector, reason: str | None = None) -> None:
        self_info = await self.account.connection.call(
            "get", f"guilds/{target.pattern['guild']}/members/{self.account.route['account']}", {}
        )
        effective = bool({"2", "4", "5"} & set(self_info["roles"]))
        if not effective:
            raise PermissionError(permission_error_message(f"remove_member@{target.path}", "read", ["manage"]))
        await self.account.connection.call(
            "delete", f"guilds/{target.pattern['guild']}/members/{target.pattern['member']}", {}
        )
