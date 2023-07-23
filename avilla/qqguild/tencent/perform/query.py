from __future__ import annotations

from typing import TYPE_CHECKING, Callable, cast

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from ..account import QQGuildAccount  # noqa
    from ..protocol import QQGuildProtocol  # noqa


class QQGuildQueryPerform((m := AccountCollector["QQGuildProtocol", "QQGuildAccount"]())._):
    m.post_applying = True

    @CoreCapability.query.collect(m, "channel", "land.guild")
    async def query_guild_channels(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        result = await self.account.connection.call("get", f"guilds/{previous.pattern['guild']}/channels", {})
        result = cast(list, result)
        for i in result:
            channel_id = str(i["id"])
            if callable(predicate) and predicate("channel", channel_id) or channel_id == predicate:
                yield previous.channel(channel_id)

    @CoreCapability.query.collect(m, "user", "land.guild")
    async def query_guild_members(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        result = await self.account.connection.call("get", f"guilds/{previous.pattern['guild']}/members", {})
        result = cast(list, result)
        for i in result:
            user_id = str(i["user"]["id"])
            if callable(predicate) and predicate("user", user_id) or user_id == predicate:
                yield previous.user(user_id)

    @CoreCapability.query.collect(m, "user", "land.guild.role")
    async def query_guild_role_members(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        result = await self.account.connection.call(
            "get", f"guilds/{previous.pattern['guild']}/roles/{previous.pattern['role']}/members", {}
        )
        for i in result["data"]:
            user_id = str(i["user"]["id"])
            if callable(predicate) and predicate("user", user_id) or user_id == predicate:
                yield Selector().land(self.account.route["land"]).guild(previous.pattern["guild"]).user(user_id)

    @CoreCapability.query.collect(m, "role", "land.guild")
    async def query_guild_roles(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        result = await self.account.connection.call("get", f"guilds/{previous.pattern['guild']}/roles", {})
        for i in result["roles"]:
            role_id = str(i["id"])
            if callable(predicate) and predicate("role", role_id) or role_id == predicate:
                yield previous.role(role_id)

    @CoreCapability.query.collect(m, "role", "land.guild.user")
    async def query_guild_user_roles(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        user = await self.account.connection.call(
            "get", f"guilds/{previous.pattern['guild']}/members/{previous.pattern['user']}", {}
        )
        for i in user["roles"]:
            role_id = str(i)
            if callable(predicate) and predicate("role", role_id) or role_id == predicate:
                yield previous.into("land.guild").role(role_id)
