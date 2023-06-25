from __future__ import annotations

from typing import TYPE_CHECKING, Any

from avilla.core._vendor.dataclasses import dataclass, field
from avilla.core.selector import Selector
from avilla.core.ryanvk import Isolate

if TYPE_CHECKING:
    from avilla.core.context import Context
    from avilla.core.protocol import BaseProtocol
    from avilla.core.platform import Platform
    from avilla.core.application import Avilla


@dataclass
class AccountInfo:
    route: Selector
    account: AbstractAccount
    protocol: BaseProtocol
    platform: Platform
    isolate: Isolate = field(default_factory=Isolate)
    enabled_message_cache: bool = False


@dataclass
class AbstractAccount:
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
