from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from graia.amnesia.message import MessageChain as MessageChain

from avilla.core.selectors import entity
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import message as message_selector

if TYPE_CHECKING:
    from avilla.core.platform import Platform

@dataclass
class Message:
    id: str
    mainline: mainline_selector
    sender: entity
    content: MessageChain
    time: datetime
    reply: message_selector | None = None

    @property
    def platform(self) -> Platform | None:
        return self.mainline.path.get("platform")

    def to_selector(self) -> "message_selector":
        return message_selector.mainline[self.mainline]._[self.id]
