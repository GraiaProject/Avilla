from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from avilla.core.exceptions import permission_error_message
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.qqapi.const import PRIVILEGE_TRANS
from avilla.standard.core.privilege import MuteCapability, MuteInfo, Privilege
from avilla.standard.core.profile import Avatar, Nick, Summary
from avilla.standard.core.relation import SceneCapability

if TYPE_CHECKING:
    from avilla.qqapi.account import QQAPIAccount  # noqa
    from avilla.qqapi.protocol import QQAPIProtocol  # noqa


class QQAPIGuildMemberActionPerform((m := AccountCollector["QQAPIProtocol", "QQAPIAccount"]())._):
    m.namespace = "avilla.protocol/qqapi::action"
    m.identify = "guild_member"

    @m.pull("land.guild.member", Nick)
    @m.pull("land.guild.channel.member", Nick)
    async def get_nick(self, target: Selector, route: ...) -> Nick:
        result = await self.account.connection.call_http(
            "get", f"guilds/{target.pattern['guild']}/members/{target.pattern['member']}", {}
        )
        return Nick(result["user"]["username"], result["nick"], None)

    @m.pull("land.guild.member", Summary)
    @m.pull("land.guild.channel.member", Summary)
    async def get_summary(self, target: Selector, route: ...) -> Summary:
        result = await self.account.connection.call_http(
            "get", f"guilds/{target.pattern['guild']}/members/{target.pattern['member']}", {}
        )
        return Summary(result["user"]["username"], result["nick"])

    @m.pull("land.guild.member", Avatar)
    @m.pull("land.guild.channel.member", Avatar)
    async def get_avatar(self, target: Selector, route: ...) -> Avatar:
        result = await self.account.connection.call_http(
            "get", f"guilds/{target.pattern['guild']}/members/{target.pattern['member']}", {}
        )
        return Avatar(result["user"]["avatar"])

    @m.pull("land.guild.channel.member", Privilege)
    async def get_privilege(self, target: Selector, route: ...) -> Privilege:
        self_info = await self.account.connection.call_http(
            "get", f"guilds/{target.pattern['guild']}/members/{self.account.route['account']}", {}
        )
        target_info = await self.account.connection.call_http(
            "get", f"guilds/{target.pattern['guild']}/members/{target.pattern['member']}", {}
        )
        effective = False
        if "4" in self_info["roles"]:
            effective = True
        elif "2" in self_info["roles"] and "4" not in target_info["roles"] and "2" not in target_info["roles"]:
            effective = True
        elif "5" in self_info["roles"] and target_info["roles"] == ["1"]:
            effective = True
        apis = await self.account.connection.call_http("get", f"guilds/{target.pattern['guild']}/api_permission", {})
        for api in apis["apis"]:
            if api["path"] == "/channels/{channel_id}/members/{user_id}/permissions" and api["method"] == "GET":
                self_permission = await self.account.connection.call_http(
                    "get",
                    f"channels/{target.pattern['channel']}/members/{self.account.route['account']}/permissions",
                    {},
                )
                result = await self.account.connection.call_http(
                    "get", f"channels/{target.pattern['channel']}/members/{target.pattern['member']}/permissions", {}
                )
                return Privilege(
                    int(result["permissions"]) & 2 == 2,
                    effective or (int(self_permission["permissions"]) & 2 == 2),
                )
        raise PermissionError(permission_error_message(f"get_permission@{target.path}", "read", ["manage"]))

    @m.pull("land.guild.channel.member", Privilege >> Summary)
    async def get_privilege_summary(self, target: Selector, route: ...) -> Summary:
        apis = await self.account.connection.call_http("get", f"guilds/{target.pattern['guild']}/api_permission", {})
        for api in apis["apis"]:
            if api["path"] == "/channels/{channel_id}/members/{user_id}/permissions" and api["method"] == "GET":
                result = await self.account.connection.call_http(
                    "get", f"channels/{target.pattern['channel']}/members/{target.pattern['member']}/permissions", {}
                )
                return Summary(
                    PRIVILEGE_TRANS[int(result["permissions"])],
                    "user's permissions in channel",
                )
        raise PermissionError(permission_error_message(f"get_permission@{target.path}", "read", ["manage"]))

    @m.pull("land.guild.channel.member", MuteInfo)
    async def get_mute_info(self, target: Selector, route: ...) -> MuteInfo:
        apis = await self.account.connection.call_http("get", f"guilds/{target.pattern['guild']}/api_permission", {})
        for api in apis["apis"]:
            if api["path"] == "/channels/{channel_id}/members/{user_id}/permissions" and api["method"] == "GET":
                result = await self.account.connection.call_http(
                    "get", f"channels/{target.pattern['channel']}/members/{target.pattern['member']}/permissions", {}
                )
                return MuteInfo(
                    int(result["permissions"]) & 4 == 4,
                    timedelta(seconds=0),
                )
        raise PermissionError(permission_error_message(f"get_permission@{target.path}", "read", ["manage"]))

    @MuteCapability.mute.collect(m, target="land.guild.channel.member")
    async def mute(self, target: Selector, duration: timedelta) -> None:
        if not (await self.get_privilege(target, Privilege)).effective:
            self_info = await self.get_privilege_summary(
                target.into(f"~.member{self.account.route['account']}"), Summary
            )
            raise PermissionError(permission_error_message(f"set_permission@{target.path}", self_info.name, ["manage"]))
        await self.account.connection.call_http(
            "put",
            f"channels/{target.pattern['channel']}/members/{target.pattern['member']}/permissions",
            {"add": 0, "remove": 4},
        )

    @MuteCapability.unmute.collect(m, target="land.guild.channel.member")
    async def unmute(self, target: Selector) -> None:
        if not (await self.get_privilege(target, Privilege)).effective:
            self_info = await self.get_privilege_summary(
                target.into(f"~.member{self.account.route['account']}"), Summary
            )
            raise PermissionError(permission_error_message(f"set_permission@{target.path}", self_info.name, ["manage"]))
        await self.account.connection.call_http(
            "put",
            f"channels/{target.pattern['channel']}/members/{target.pattern['member']}/permissions",
            {"add": 4, "remove": 0},
        )

    @SceneCapability.remove_member.collect(m, target="land.guild.member")
    @SceneCapability.remove_member.collect(m, target="land.guild.channel.member")
    async def remove_member(self, target: Selector, reason: str | None = None, permanent: bool = False) -> None:
        self_info = await self.account.connection.call_http(
            "get", f"guilds/{target.pattern['guild']}/members/{self.account.route['account']}", {}
        )
        effective = bool({"2", "4", "5"} & set(self_info["roles"]))
        if not effective:
            raise PermissionError(permission_error_message(f"remove_member@{target.path}", "read", ["manage"]))
        await self.account.connection.call_http(
            "delete", f"guilds/{target.pattern['guild']}/members/{target.pattern['member']}", {}
        )
