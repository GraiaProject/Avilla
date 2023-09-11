from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.core.context import Context
from avilla.core.builtins.capability import CoreCapability

if TYPE_CHECKING:
    from avilla.console.account import ConsoleAccount  # noqa
    from avilla.console.protocol import ConsoleProtocol  # noqa


class ConsoleContextPerform((m := AccountCollector["ConsoleProtocol", "ConsoleAccount"]())._):
    m.post_applying = True

    @CoreCapability.get_context.collect(m, "land.user")
    def get_context_from_channel(self, target: Selector, *, via: Selector | None = None):
        context = Context(
            account=self.account,
            client=target,
            endpoint=self.account.route,
            scene=target,
            selft=self.account.route,
        )
