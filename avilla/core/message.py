from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from graia.amnesia.message import MessageChain as MessageChain

from avilla.core.selectors import entity
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import message as message_selector


@dataclass
class Message:
    id: str
    mainline: mainline_selector
    sender: entity
    content: MessageChain
    time: datetime
    reply: message_selector | None = None

    def to_selector(self) -> "message_selector":
        return message_selector.mainline[self.mainline]._[self.id]
