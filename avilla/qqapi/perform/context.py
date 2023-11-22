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
