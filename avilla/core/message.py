from __future__ import annotations

from typing import TYPE_CHECKING, cast

from graia.amnesia.message import MessageChain

from avilla.core._vendor.dataclasses import dataclass
from avilla.core.platform import Land
from avilla.core.selector import Selector
from avilla.standard.core.message.skeleton import MessageRevoke

from ._runtime import cx_context
from .metadata import Metadata

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(slots=True)
class Message(Metadata):
    id: str
    scene: Selector
    sender: Selector
    content: MessageChain
    time: datetime
    reply: Selector | None = None

    @property
    def land(self):
        return Land(cast(str, self.scene.pattern.get("land")))

    def to_selector(self) -> Selector:
        return self.scene.message(self.id)

    async def revoke(self):
        await cx_context.get()[MessageRevoke.revoke](self)
