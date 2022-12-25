from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from graia.amnesia.message import __message_chain_class__

from avilla.core.platform import Land
from avilla.core.selector import Selector

from ..spec.core.message.skeleton import MessageRevoke
from .metadata import Metadata

if TYPE_CHECKING:
    from datetime import datetime


@dataclass
class Message(Metadata):
    id: str
    scene: Selector
    sender: Selector
    content: __message_chain_class__
    time: datetime
    reply: Selector | None = None

    @property
    def land(self):
        return Land(cast(str, self.scene.pattern.get("land")))

    def to_selector(self) -> Selector:
        return self.scene.message(self.id)

    def rev(self):
        return self.to_selector().rev()

    async def revoke(self):
        return await self.rev().wrap(MessageRevoke).revoke()
