from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.core.context import Context
from avilla.core.builtins.capability import CoreCapability

if TYPE_CHECKING:
    from avilla.elizabeth.account import ElizabethAccount  # noqa
    from avilla.elizabeth.protocol import ElizabethProtocol  # noqa


class ElizabethContextPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.post_applying = True

    @CoreCapability.get_context.collect(m, "land.group.member")
    def get_context_from_member(self, target: Selector, *, via: Selector | None = None):
        if "land" not in target:
            target = target.land(self.account.route["land"])
        if target.path == "land.group":
            return Context(
                self.account, 
                target, 
                target, 
                target,
                target.member(self.account.route["account"]),
            )
        elif target.path == "land.friend":
            return Context(
                self.account, 
                target,
                self.account.route, 
                target,
                self.account.route
            )
        elif target.path == "land.group.member":
            return Context(
                self.account,
                target,
                target.into("::group"),
                target.into("::group"),
                target.into(f"~.member({self.account.route['account']})"),
            )
        else:
            raise NotImplementedError()