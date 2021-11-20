from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from avilla.core.contactable import Contactable

from avilla.core.mainline import Mainline
from avilla.core.message.chain import MessageChain


@dataclass
class Message:
    id: str
    mainline: Mainline
    sender: Contactable
    content: MessageChain
    time: datetime
    reply: Optional[str] = None
