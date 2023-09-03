from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.core.context import Context
from avilla.core.builtins.capability import CoreCapability

if TYPE_CHECKING:
    from avilla.qqguild.tencent.account import QQGuildAccount  # noqa
    from avilla.qqguild.tencent.protocol import QQGuildProtocol  # noqa


class QQGuildContextPerform((m := AccountCollector["QQGuildProtocol", "QQGuildAccount"]())._):
    m.post_applying = True

    @CoreCapability.get_context.collect(m, "land.guild.channel")
    def get_context_from_channel(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target,
            target,
            target.member(self.account.route["account"]),
        )

    @CoreCapability.get_context.collect(m, "land.guild.channel.member")
    def get_context_from_member(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target.into("::guild.channel"),
            target.into("::guild.channel"),
            target.into(f"~.member({self.account.route['account']})"),
        )

    @CoreCapability.get_context.collect(m, "land.guild.user")
    def get_context_from_user(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            self.account.route,
            target,
            self.account.route
        )
