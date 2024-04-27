from dataclasses import dataclass

from avilla.core import Metadata


@dataclass
class MessageAutoDeleteTimer(Metadata):
    message_auto_delete_time: int
