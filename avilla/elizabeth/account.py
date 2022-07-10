from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.account import AbstractAccount
from avilla.core.relationship import Relationship
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from .protocol import ElizabethProtocol


class ElizabethAccount(AbstractAccount):
    protocol: ElizabethProtocol

    async def get_relationship(self, target: Selector) -> Relationship:
        if target.path == "land.group":
            return Relationship(self.protocol, target, target, self.to_selector())
        elif target.path == "land.group.member":
            return Relationship(
                self.protocol,
                target,
                Selector().land(self.land.name).group(target.pattern["group"]),
                self.to_selector(),
            )
        elif target.path == "land.friend":
            return Relationship(self.protocol, target, target, self.to_selector())
        else:
            raise NotImplementedError()

    @property
    def available(self) -> bool:
        ...  # TODO: lookup in service, use status
