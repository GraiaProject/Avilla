from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.core.context import Context
from avilla.core.builtins.capability import CoreCapability

if TYPE_CHECKING:
    from avilla.red.account import RedAccount  # noqa
    from avilla.red.protocol import RedProtocol  # noqa


class RedContextPerform((m := AccountCollector["RedProtocol", "RedAccount"]())._):
    m.post_applying = True

    @CoreCapability.get_context.collect(m, "land.group")
    def get_context_from_group(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target,
            target,
            target.member(self.account.route["account"]),
        )

    @CoreCapability.get_context.collect(m, "land.friend")
    def get_context_from_friend(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            self.account.route,
            target,
            self.account.route
        )

    @CoreCapability.get_context.collect(m, "land.group.member")
    def get_context_from_member(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target.into("::group"),
            target.into("::group"),
            target.into(f"~.member({self.account.route['account']})"),
        )
