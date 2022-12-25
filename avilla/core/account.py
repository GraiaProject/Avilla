from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from avilla.core.platform import Land
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from avilla.core.context import Context
    from avilla.core.protocol import BaseProtocol


@dataclass
class AbstractAccount(ABC):
    id: str
    land: Land
    protocol: BaseProtocol

    def __init__(self, id: str, protocol: BaseProtocol, land: Land | None = None):
        self.id = id
        self.land = land or protocol.land
        self.protocol = protocol

    @abstractmethod
    async def get_context(self, target: Selector, *, via: Selector | None = None) -> Context:
        ...

    @abstractmethod
    async def call(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        ...

    def get_self_context(self):
        from avilla.core.context import Context

        selector = self.to_selector()
        return Context(
            self,
            selector,
            selector,
            Selector().land(self.land.name),
            selector,
        )

    @property
    def available(self) -> bool:
        return True

    def to_selector(self) -> Selector:
        return Selector().land(self.land.name).account(self.id)

    def is_anonymous(self) -> bool:
        return self.id == "anonymous"

    def __eq__(self, other: AbstractAccount):
        return (
            self.__class__ is other.__class__
            and self.id == other.id
            and self.land == other.land
            and self.protocol == other.protocol
        )
