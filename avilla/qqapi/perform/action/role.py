from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from avilla.core.exceptions import permission_error_message
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.qqapi.const import PRIVILEGE_TRANS
from avilla.qqapi.role import (
    Role,
    RoleCreate,
    RoleDelete,
    RoleEdit,
    RoleMemberCapability,
)
from avilla.standard.core.common import Count
from avilla.standard.core.privilege import MuteCapability, MuteInfo, Privilege
from avilla.standard.core.profile import Summary, SummaryCapability

if TYPE_CHECKING:
    from avilla.qqapi.account import QQAPIAccount  # noqa
    from avilla.qqapi.protocol import QQAPIProtocol  # noqa


class QQAPIRoleActionPerform((m := AccountCollector["QQAPIProtocol", "QQAPIAccount"]())._):
    m.namespace = "avilla.protocol/qqapi::action"
    m.identify = "role"

    @m.pull("land.guild.role", Role)
    async def get_role(self, target: Selector, route: ...) -> Role:
        result = await self.account.connection.call_http("get", f"guilds/{target.pattern['guild']}/roles", {})
        for role in result["roles"]:
            if role["id"] == target.pattern["role"]:
                return Role(role["id"], target.into("land.guild"), role["name"], bool(role["hoist"]), role["color"])
        raise ValueError(f"Role {target.pattern['role']} not found")

    @m.pull("land.guild.role", Summary)
    async def get_role_summary(self, target: Selector, route: ...) -> Summary:
        return Summary(
            (await self.get_role(target, Role)).name,
            "name of role",
        )

    @m.pull("land.guild.role", Role >> Summary)
    async def get_role_summary1(self, target: Selector, route: ...) -> Summary:
        return (await self.get_role_summary(target, Summary)).infers(Role >> Summary)

    @m.pull("land.guild.role", Count)
    async def get_role_count(self, target: Selector, route: ...) -> Count:
        result = await self.account.connection.call_http("get", f"guilds/{target.pattern['guild']}/roles", {})
        for role in result["roles"]:
            if role["id"] == target.pattern["role"]:
                return Count(role["number"], role["member_limit"])
        raise ValueError(f"Role {target.pattern['role']} not found")

    @m.pull("land.guild.role", Role >> Count)
    async def get_role_count1(self, target: Selector, route: ...) -> Count:
        return (await self.get_role_count(target, Count)).infers(Role >> Count)

    @m.pull("land.guild.role", Privilege)
    async def get_privilege(self, target: Selector, route: ...) -> Privilege:
        self_info = await self.account.connection.call_http(
            "get", f"guilds/{target.pattern['guild']}/members/{self.account.route['account']}", {}
        )
        effective = bool({"2", "4", "5"} & set(self_info["roles"]))
        apis = await self.account.connection.call_http("get", f"guilds/{target.pattern['guild']}/api_permission", {})
        for api in apis["apis"]:
            if api["path"] == "/channels/{channel_id}/roles/{role_id}/permissions" and api["method"] == "GET":
                result = await self.account.connection.call_http(
                    "get", f"channels/{target.pattern['channel']}/roles/{target.pattern['role']}/permissions", {}
                )
                return Privilege(
                    int(result["permissions"]) & 2 == 2,
                    effective,
                )
        raise PermissionError(permission_error_message(f"get_permission@{target.path}", "read", ["manage"]))

    @m.pull("land.guild.role", Role >> Privilege)
    async def get_privilege1(self, target: Selector, route: ...) -> Privilege:
        return (await self.get_privilege(target, Privilege)).infers(Role >> Privilege)

    @m.pull("land.guild.role", Privilege >> Summary)
    async def get_privilege_summary(self, target: Selector, route: ...) -> Summary:
        apis = await self.account.connection.call_http("get", f"guilds/{target.pattern['guild']}/api_permission", {})
        for api in apis["apis"]:
            if api["path"] == "/channels/{channel_id}/roles/{role_id}/permissions" and api["method"] == "GET":
                result = await self.account.connection.call_http(
                    "get", f"channels/{target.pattern['channel']}/roles/{target.pattern['role']}/permissions", {}
                )
                return Summary(
                    PRIVILEGE_TRANS[int(result["permissions"])],
                    "user's permissions in channel",
                )
        raise PermissionError(permission_error_message(f"get_permission@{target.path}", "read", ["manage"]))

    @m.pull("land.guild.role", Role >> Privilege >> Summary)
    async def get_privilege_summary1(self, target: Selector, route: ...) -> Summary:
        return (await self.get_privilege_summary(target, Summary)).infers(Role >> Privilege >> Summary)

    @m.pull("land.guild.role", MuteInfo)
    async def get_mute_info(self, target: Selector, route: ...) -> MuteInfo:
        apis = await self.account.connection.call_http("get", f"guilds/{target.pattern['guild']}/api_permission", {})
        for api in apis["apis"]:
            if api["path"] == "/channels/{channel_id}/roles/{role_id}/permissions" and api["method"] == "GET":
                result = await self.account.connection.call_http(
                    "get", f"channels/{target.pattern['channel']}/roles/{target.pattern['role']}/permissions", {}
                )
                return MuteInfo(
                    int(result["permissions"]) & 4 == 4,
                    timedelta(seconds=0),
                )
        raise PermissionError(permission_error_message(f"get_permission@{target.path}", "read", ["manage"]))

    @MuteCapability.mute.collect(m, target="land.guild.role")
    async def mute(self, target: Selector, duration: timedelta) -> None:
        if not (await self.get_privilege(target, Privilege)).effective:
            raise PermissionError(permission_error_message(f"set_permission@{target.path}", "read", ["manage"]))
        await self.account.connection.call_http(
            "put",
            f"channels/{target.pattern['channel']}/roles/{target.pattern['role']}/permissions",
            {"add": 0, "remove": 4},
        )

    @MuteCapability.unmute.collect(m, target="land.guild.role")
    async def unmute(self, target: Selector) -> None:
        if not (await self.get_privilege(target, Privilege)).effective:
            raise PermissionError(permission_error_message(f"set_permission@{target.path}", "read", ["manage"]))
        await self.account.connection.call_http(
            "put",
            f"channels/{target.pattern['channel']}/roles/{target.pattern['role']}/permissions",
            {"add": 4, "remove": 0},
        )

    @RoleCreate.create.collect(m, target="land.guild")
    async def create_role(
        self, target: Selector, name: str, hoist: bool | None = None, color: int | None = None
    ) -> Selector:
        self_info = await self.account.connection.call_http(
            "get", f"guilds/{target.pattern['guild']}/members/{self.account.route['account']}", {}
        )
        effective = bool({"2", "4", "5"} & set(self_info["roles"]))
        if not effective:
            raise PermissionError(permission_error_message(f"create_role@{target.path}", "read", ["manage"]))
        data: dict = {"name": name}
        if hoist is not None:
            data["hoist"] = hoist
        if color is not None:
            data["color"] = color
        result = await self.account.connection.call_http("post", f"guilds/{target.pattern['guild']}/roles", data)
        return target.role(result["role_id"])

    @RoleDelete.delete.collect(m, target="land.guild.role")
    async def delete_role(self, target: Selector) -> None:
        self_info = await self.account.connection.call_http(
            "get", f"guilds/{target.pattern['guild']}/members/{self.account.route['account']}", {}
        )
        effective = bool({"2", "4", "5"} & set(self_info["roles"]))
        if not effective:
            raise PermissionError(permission_error_message(f"delete_role@{target.path}", "read", ["manage"]))
        await self.account.connection.call_http(
            "delete", f"guilds/{target.pattern['guild']}/roles/{target.pattern['role']}", {}
        )

    @SummaryCapability.set_name.collect(m, target="land.guild.role", route=Summary)
    async def set_name(self, target: Selector, route: ..., name: str) -> None:
        self_info = await self.account.connection.call_http(
            "get", f"guilds/{target.pattern['guild']}/members/{self.account.route['account']}", {}
        )
        effective = bool({"2", "4", "5"} & set(self_info["roles"]))
        if not effective:
            raise PermissionError(permission_error_message(f"set_name@{target.path}", "read", ["manage"]))
        await self.account.connection.call_http(
            "patch", f"guilds/{target.pattern['guild']}/roles/{target.pattern['role']}", {"name": name}
        )

    @RoleEdit.edit.collect(m, target="land.guild.role")
    async def edit_role(
        self, target: Selector, name: str | None = None, hoist: bool | None = None, color: int | None = None
    ) -> None:
        self_info = await self.account.connection.call_http(
            "get", f"guilds/{target.pattern['guild']}/members/{self.account.route['account']}", {}
        )
        effective = bool({"2", "4", "5"} & set(self_info["roles"]))
        if not effective:
            raise PermissionError(permission_error_message(f"edit_role@{target.path}", "read", ["manage"]))
        data = {}
        if name is not None:
            data["name"] = name
        if hoist is not None:
            data["hoist"] = hoist
        if color is not None:
            data["color"] = color
        await self.account.connection.call_http(
            "patch", f"guilds/{target.pattern['guild']}/roles/{target.pattern['role']}", data
        )

    @RoleMemberCapability.add.collect(m, target="land.guild.user")
    async def add_role_user(self, target: Selector, member: Selector) -> None:
        role_id = target.pattern["role"]
        if role_id == "5":
            raise ValueError("missing target: channel")
        await self.account.connection.call_http(
            "put", f"guilds/{target.pattern['guild']}/members/{member.pattern['user']}/roles/{role_id}", {}
        )

    @RoleMemberCapability.add.collect(m, target="land.guild.member")
    async def add_role_member(self, target: Selector, member: Selector) -> None:
        role_id = target.pattern["role"]
        if role_id == "5":
            raise ValueError("missing target: channel")
        await self.account.connection.call_http(
            "put", f"guilds/{target.pattern['guild']}/members/{member.pattern['member']}/roles/{role_id}", {}
        )

    @RoleMemberCapability.add.collect(m, target="land.guild.channel.member")
    async def add_role_member1(self, target: Selector, member: Selector) -> None:
        role_id = target.pattern["role"]
        await self.account.connection.call_http(
            "put",
            f"guilds/{target.pattern['guild']}/members/{member.pattern['member']}/roles/{role_id}",
            {"channel": {"id": target.pattern["channel"]}} if role_id == "5" else {},
        )

    @RoleMemberCapability.remove.collect(m, target="land.guild.user")
    async def remove_role_user(self, target: Selector, member: Selector) -> None:
        role_id = target.pattern["role"]
        if role_id == "5":
            raise ValueError("missing target: channel")
        await self.account.connection.call_http(
            "delete", f"guilds/{target.pattern['guild']}/members/{member.pattern['user']}/roles/{role_id}", {}
        )

    @RoleMemberCapability.remove.collect(m, target="land.guild.member")
    async def remove_role_member(self, target: Selector, member: Selector) -> None:
        role_id = target.pattern["role"]
        if role_id == "5":
            raise ValueError("missing target: channel")
        await self.account.connection.call_http(
            "delete", f"guilds/{target.pattern['guild']}/members/{member.pattern['member']}/roles/{role_id}", {}
        )

    @RoleMemberCapability.remove.collect(m, target="land.guild.channel.member")
    async def remove_role_member1(self, target: Selector, member: Selector) -> None:
        role_id = target.pattern["role"]
        await self.account.connection.call_http(
            "delete",
            f"guilds/{target.pattern['guild']}/members/{member.pattern['member']}/roles/{role_id}",
            {"channel": {"id": target.pattern["channel"]}} if role_id == "5" else {},
        )
