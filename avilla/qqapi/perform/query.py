from __future__ import annotations

from typing import TYPE_CHECKING, Callable, cast

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from ..account import QQAPIAccount  # noqa
    from ..protocol import QQAPIProtocol  # noqa


class QQAPIQueryPerform((m := AccountCollector["QQAPIProtocol", "QQAPIAccount"]())._):
    m.namespace = "avilla.protocol/qqapi::query"

    @m.entity(CoreCapability.query, target="land.guild")
    async def query_guilds(self, predicate: Callable[[str, str], bool] | str, previous: None):
        result = await self.account.connection.call_http("get", f"users/@me/guilds", {})
        result = cast(list, result)
        for i in result:
            guild_id = str(i["id"])
            if callable(predicate) and predicate("guild", guild_id) or guild_id == predicate:
                yield Selector().land(self.account.route["land"]).guild(guild_id)

    @m.entity(CoreCapability.query, target="channel", previous="land.guild")
    async def query_guild_channels(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        result = await self.account.connection.call_http("get", f"guilds/{previous.pattern['guild']}/channels", {})
        result = cast(list, result)
        for i in result:
            channel_id = str(i["id"])
            if callable(predicate) and predicate("channel", channel_id) or channel_id == predicate:
                yield previous.channel(channel_id)

    @m.entity(CoreCapability.query, target="member", previous="land.guild")
    async def query_guild_users(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        result = await self.account.connection.call_http("get", f"guilds/{previous.pattern['guild']}/members", {})
        result = cast(list, result)
        for i in result:
            user_id = str(i["user"]["id"])
            if callable(predicate) and predicate("member", user_id) or user_id == predicate:
                yield previous.member(user_id)

    @m.entity(CoreCapability.query, target="member", previous="land.guild.channel")
    async def query_guild_members(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        result = await self.account.connection.call_http("get", f"guilds/{previous.pattern['guild']}/members", {})
        result = cast(list, result)
        for i in result:
            user_id = str(i["user"]["id"])
            if callable(predicate) and predicate("member", user_id) or user_id == predicate:
                yield previous.member(user_id)

    @m.entity(CoreCapability.query, target="member", previous="land.group")
    async def query_group_members(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        result = await self.account.connection.call_http("post", f"v2/groups/{previous.pattern['group']}/members", {})
        for i in result["members"]:
            member_id = str(i["member_openid"])
            if callable(predicate) and predicate("member", member_id) or member_id == predicate:
                yield previous.member(member_id)

    @m.entity(CoreCapability.query, target="member", previous="land.guild.role")
    async def query_guild_role_members(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        result = await self.account.connection.call_http(
            "get", f"guilds/{previous.pattern['guild']}/roles/{previous.pattern['role']}/members", {}
        )
        for i in result["data"]:
            user_id = str(i["user"]["id"])
            if callable(predicate) and predicate("member", user_id) or user_id == predicate:
                yield Selector().land(self.account.route["land"]).guild(previous.pattern["guild"]).member(user_id)

    @m.entity(CoreCapability.query, target="role", previous="land.guild")
    async def query_guild_roles(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        result = await self.account.connection.call_http("get", f"guilds/{previous.pattern['guild']}/roles", {})
        for i in result["roles"]:
            role_id = str(i["id"])
            if callable(predicate) and predicate("role", role_id) or role_id == predicate:
                yield previous.role(role_id)

    @m.entity(CoreCapability.query, target="role", previous="land.guild.user")
    async def query_guild_user_roles(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        user = await self.account.connection.call_http(
            "get", f"guilds/{previous.pattern['guild']}/members/{previous.pattern['user']}", {}
        )
        for i in user["roles"]:
            role_id = str(i)
            if callable(predicate) and predicate("role", role_id) or role_id == predicate:
                yield previous.into("land.guild").role(role_id)
