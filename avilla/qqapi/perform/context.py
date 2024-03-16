from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.builtins.capability import CoreCapability
from avilla.core.context import Context
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from avilla.qqapi.account import QQAPIAccount  # noqa
    from avilla.qqapi.protocol import QQAPIProtocol  # noqa


class QQAPIContextPerform((m := AccountCollector["QQAPIProtocol", "QQAPIAccount"]())._):
    m.namespace = "avilla.protocol/qqapi::context"

    @m.entity(CoreCapability.get_context, target="land.guild.channel")
    def get_context_from_channel(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target,
            target,
            target.member(self.account.route["account"]),
        )

    @m.entity(CoreCapability.get_context, target="land.guild.channel.member")
    def get_context_from_guild_member(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target.into("::guild.channel"),
            target.into("::guild.channel"),
            target.into(f"~.member({self.account.route['account']})"),
        )

    @m.entity(CoreCapability.get_context, target="land.guild.member")
    def get_context_from_member(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target.into("::guild"),
            target.into("::guild"),
            target.into(f"~.member({self.account.route['account']})"),
        )

    @m.entity(CoreCapability.get_context, target="land.guild.user")
    def get_context_from_guild_user(self, target: Selector, *, via: Selector | None = None):
        return Context(self.account, target, self.account.route, target, self.account.route)

    @m.entity(CoreCapability.get_context, target="land.group")
    def get_context_from_group(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target,
            target,
            target.member(self.account.route["account"]),
        )

    @m.entity(CoreCapability.get_context, target="land.friend")
    def get_context_from_friend(self, target: Selector, *, via: Selector | None = None):
        if via:
            return Context(
                self.account,
                via,
                target,
                target,
                self.account.route,
            )
        return Context(self.account, target, self.account.route, target, self.account.route)

    @m.entity(CoreCapability.get_context, target="land.group.member")
    def get_context_from_group_member(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target.into("::group"),
            target.into("::group"),
            target.into(f"~.member({self.account.route['account']})"),
        )

    @m.entity(CoreCapability.channel, target="land.group")
    @m.entity(CoreCapability.channel, target="land.group.member")
    def channel_from_group(self, target: Selector):
        return target["group"]

    @m.entity(CoreCapability.guild, target="land.group")
    @m.entity(CoreCapability.guild, target="land.group.member")
    def guild_from_group(self, target: Selector):
        return target["group"]

    @m.entity(CoreCapability.channel, target="land.guild.channel")
    @m.entity(CoreCapability.channel, target="land.guild.channel.member")
    def channel_from_guild_channel(self, target: Selector):
        return target["channel"]

    @m.entity(CoreCapability.user, target="land.guild.user")
    @m.entity(CoreCapability.channel, target="land.guild.user")
    def user_from_guild_user(self, target: Selector):
        return target["user"]

    @m.entity(CoreCapability.guild, target="land.guild")
    @m.entity(CoreCapability.guild, target="land.guild.user")
    @m.entity(CoreCapability.guild, target="land.guild.member")
    @m.entity(CoreCapability.guild, target="land.guild.channel")
    @m.entity(CoreCapability.guild, target="land.guild.channel.member")
    def guild_from_guild_channel(self, target: Selector):
        return target["guild"]

    @m.entity(CoreCapability.user, target="land.group.member")
    @m.entity(CoreCapability.user, target="land.guild.member")
    @m.entity(CoreCapability.user, target="land.guild.channel.member")
    def user_from_member(self, target: Selector):
        return target["member"]

    @m.entity(CoreCapability.user, target="land.friend")
    @m.entity(CoreCapability.channel, target="land.friend")
    def user_from_friend(self, target: Selector):
        return target["friend"]
