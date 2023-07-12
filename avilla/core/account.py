from __future__ import annotations

from typing import TYPE_CHECKING, Any

from statv import Stats, Statv

from avilla.core._vendor.dataclasses import dataclass, field
from avilla.core.ryanvk import Isolate
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
    isolate: Isolate = field(default_factory=Isolate)
    enabled_message_cache: bool = False


@dataclass
class BaseAccount:
    route: Selector
    avilla: Avilla

    async def get_context(self, target: Selector, *, via: Selector | None = None) -> Context:
        raise NotImplementedError

    async def call(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        raise NotImplementedError

    @property
    def info(self) -> AccountInfo:
        return self.avilla.accounts[self.route]

    def get_self_context(self):
        from avilla.core.context import Context

        return Context(
            self,
            self.route,
            self.route,
            self.route.into("::"),
            self.route,
        )

    @property
    def available(self) -> bool:
        return True

    def get_ryanvk_components(self):
        return {
            "account": self,
            "protocol": self.info.protocol,
            "avilla": self.avilla
        }


class AccountStatus(Statv):
    enabled = Stats[bool]("enabled", default=False)

    @property
    def available(self) -> bool:
        return self.enabled
