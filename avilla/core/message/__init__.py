from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from avilla.core.message.chain import MessageChain
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import rsctx


@dataclass
class Message:
    id: str
    mainline: mainline_selector
    sender: rsctx
    content: MessageChain
    time: datetime
    reply: Optional[str] = None
