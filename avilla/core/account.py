from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from statv import Stats, Statv

from avilla.core.ryanvk.staff import Staff
from avilla.core.selector import Selector

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

    @property
    def info(self) -> AccountInfo:
        return self.avilla.accounts[self.route]

    @property
    def staff(self):
        return Staff(self.get_staff_artifacts(), self.get_staff_components())

    @property
    def available(self) -> bool:
        return True

    def get_context(self, target: Selector, *, via: Selector | None = None) -> Context:
        return self.staff.get_context(target, via=via)

    def get_self_context(self):
        from avilla.core.context import Context

        return Context(
            self,
            self.route,
            self.route,
            self.route.into("::"),
            self.route,
        )

    def get_staff_components(self):
        return {"account": self, "protocol": self.info.protocol, "avilla": self.avilla}

    def get_staff_artifacts(self):
        return [
            self.info.artifacts,
            self.info.protocol.artifacts,
            self.avilla.global_artifacts,
        ]

    def __staff_generic__(self, element_type: dict, event_type: dict):
        ...


class AccountStatus(Statv):
    enabled = Stats[bool]("enabled", default=False)

    @property
    def available(self) -> bool:
        return self.enabled
