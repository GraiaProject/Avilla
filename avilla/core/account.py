from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from statv import Stats, Statv

from avilla.core.selector import Selector
from avilla.core.builtins.capability import CoreCapability

if TYPE_CHECKING:
    from avilla.core.application import Avilla
    from avilla.core.context import Context
    from avilla.core.platform import Platform
    from avilla.core.protocol import BaseProtocol


@dataclass
class AccountInfo:
    route: Selector
    account: BaseAccount
    protocol: BaseProtocol
    platform: Platform
    artifacts: dict[Any, Any] = field(default_factory=dict)
    enabled_message_cache: bool = False


@dataclass
class BaseAccount:
    route: Selector
    avilla: Avilla
    artifacts: 

    @property
    def info(self) -> AccountInfo:
        return self.avilla.accounts[self.route]

    @property
    def available(self) -> bool:
        return True

    def get_context(self, target: Selector, *, via: Selector | None = None) -> Context:
        return CoreCapability.get_context(target, via=via)

    def get_self_context(self):
        from avilla.core.context import Context

        return Context(self, self.route, self.route, self.route.into("::"), self.route)


class AccountStatus(Statv):
    enabled = Stats[bool]("enabled", default=False)

    @property
    def available(self) -> bool:
        return self.enabled
