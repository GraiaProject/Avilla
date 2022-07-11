from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.account import AbstractAccount
from avilla.core.relationship import Relationship
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from .protocol import OneBot12Protocol


class OneBot12Account(AbstractAccount):
    protocol: OneBot12Protocol

    async def get_relationship(self, target: Selector) -> Relationship:
        # TODO: 对象存在性检查
        if "land" not in target:
            target = Selector().mixin("land." + target.path, target)
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
        return self.protocol.service.get_account(int(self.id)).status.available
