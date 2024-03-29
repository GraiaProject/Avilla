from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.builtins.capability import CoreCapability
from avilla.core.context import Context
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from avilla.satori.account import SatoriAccount  # noqa
    from avilla.satori.protocol import SatoriProtocol  # noqa


class SatoriContextPerform((m := AccountCollector["SatoriProtocol", "SatoriAccount"]())._):
    m.namespace = "avilla.protocol/satori::context"

    @m.entity(CoreCapability.get_context, target="land.public.channel")
    def get_context_from_public(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target,
            target,
            target.member(self.account.route["account"]),
        )

    @m.entity(CoreCapability.get_context, target="land.private.user")
    def get_context_from_user(self, target: Selector, *, via: Selector | None = None):
        return Context(self.account, target, self.account.route, target, self.account.route)

    @m.entity(CoreCapability.get_context, target="land.public.channel.member")
    def get_context_from_member(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target.into("::public.channel"),
            target.into("::public.channel"),
            target.into(f"~.member({self.account.route['account']})"),
        )

    @m.entity(CoreCapability.channel, target="land.private.user")
    def channel_from_user(self, target: Selector):
        return target["private"]

    @m.entity(CoreCapability.channel, target="land.public.channel")
    def channel_from_channel(self, target: Selector):
        return target["channel"]

    @m.entity(CoreCapability.guild, target="land.public.channel")
    def guild_from_channel(self, target: Selector):
        return target["public"]

    @m.entity(CoreCapability.user, target="land.private.user")
    def user_from_user(self, target: Selector):
        return target["user"]

    @m.entity(CoreCapability.user, target="land.public.channel.member")
    def user_from_member(self, target: Selector):
        return target["member"]
