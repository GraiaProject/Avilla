from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from graia.amnesia.message import MessageChain

from avilla.core.platform import Land
from avilla.core.selector import Selector
from avilla.standard.core.message.capability import MessageRevoke

from ._runtime import cx_context
from .metadata import Metadata


@dataclass
class Message(Metadata):
    id: str
    scene: Selector
    sender: Selector
    content: MessageChain
    time: datetime
    reply: Selector | None = None

    @property
    def land(self):
        return Land(self.scene["land"])

    def to_selector(self) -> Selector:
        return self.scene.message(self.id)

    async def revoke(self):
        await cx_context.get()[MessageRevoke.revoke](self.to_selector())
