from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast
from avilla.core.cell import Cell

from graia.amnesia.message import MessageChain

from avilla.core.platform import Land
from avilla.core.traitof import DestTraitCall, Trait, TraitCall
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from datetime import datetime


class MessageTrait(Trait):
    @DestTraitCall().bound
    async def send(self, message: MessageChain, *, reply: Selector | None = None) -> Selector:
        ...

    @TraitCall().bound
    async def revoke(self, message: Selector) -> None:
        ...

    @TraitCall().bound
    async def edit(self, message: Selector, content: MessageChain) -> None:
        ...

    # MessageFetch => rs.pull(Message, target=...)


@dataclass
class Message(Cell):
    id: str
    mainline: Selector
    sender: Selector
    content: MessageChain
    time: datetime
    reply: Selector | None = None

    @property
    def land(self):
        return Land(cast(str, self.mainline.pattern.get("land")))

    def to_selector(self) -> Selector:
        return self.mainline.copy().message(self.id)
