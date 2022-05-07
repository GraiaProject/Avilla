import copy
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Iterable, List, Optional, Type, TypeVar, Union

from avilla.core.selectors import entity
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import message as message_selector
from graia.amnesia.message import MessageChain

@dataclass
class Message:
    id: str
    mainline: mainline_selector
    sender: entity
    content: "MessageChain"
    time: datetime
    reply: Optional["message_selector"] = None

    def to_selector(self) -> "message_selector":
        return message_selector.mainline[self.mainline]._[self.id]
