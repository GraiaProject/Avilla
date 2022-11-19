
from typing import Literal

from .avilla.core.standards.message.skeleton import MessageSend

a = MessageSend[Literal[True]]()
reveal_type(a.send)