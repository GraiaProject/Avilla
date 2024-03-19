from __future__ import annotations

from typing import TYPE_CHECKING

from flywheel import scoped_collect

from avilla.core.builtins.capability import CoreCapability
from avilla.core.context import Context
from avilla.core.selector import Selector
from avilla.satori.bases import InstanceOfAccount

if TYPE_CHECKING:
    from avilla.satori.account import SatoriAccount  # noqa
    from avilla.satori.protocol import SatoriProtocol  # noqa


class SatoriContextPerform(m := scoped_collect.env().target, InstanceOfAccount, static=True):

    @m.impl(CoreCapability.get_context, target="land.guild.channel")
    def get_context_from_public(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target,
            target,
            target.member(self.account.route["account"]),
        )

    @m.impl(CoreCapability.get_context, target="land.private.user")
    def get_context_from_user(self, target: Selector, *, via: Selector | None = None):
        return Context(self.account, target, self.account.route, target, self.account.route)

    @m.impl(CoreCapability.get_context, target="land.guild.channel.member")
    def get_context_from_member(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target.into("::guild.channel"),
            target.into("::guild.channel"),
            target.into(f"~.member({self.account.route['account']})"),
        )

    @m.impl(CoreCapability.channel, target="land.private.user")
    def channel_from_user(self, target: Selector):
        return target["private"]

    @m.impl(CoreCapability.channel, target="land.guild.channel")
    def channel_from_channel(self, target: Selector):
        return target["channel"]

    @m.impl(CoreCapability.guild, target="land.guild.channel")
    def guild_from_channel(self, target: Selector):
        return target["guild"]

    @m.impl(CoreCapability.user, target="land.private.user")
    def user_from_user(self, target: Selector):
        return target["user"]

    @m.impl(CoreCapability.user, target="land.guild.channel.member")
    def user_from_member(self, target: Selector):
        return target["member"]
