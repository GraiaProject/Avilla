from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.builtins.capability import CoreCapability
from avilla.core.context import Context
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from avilla.console.account import ConsoleAccount  # noqa
    from avilla.console.protocol import ConsoleProtocol  # noqa


class ConsoleContextPerform((m := AccountCollector["ConsoleProtocol", "ConsoleAccount"]())._):
    m.namespace = "avilla.protocol/console::action/get_context"

    @CoreCapability.get_context.collect(m, target="land.user")
    def get_context_from_channel(self, target: Selector, *, via: Selector | None = None):
        return Context(
            account=self.account,
            client=target,
            endpoint=self.account.route,
            scene=target,
            selft=self.account.route,
        )

    @m.entity(CoreCapability.channel, target="land.user")
    def channel_from_channel(self, target: Selector):
        return target["user"]

    @m.entity(CoreCapability.user, target="land.user")
    def user_from_friend(self, target: Selector):
        return target["user"]
