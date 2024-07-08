from dataclasses import dataclass
from typing import Literal

from avilla.core import Metadata


@dataclass
class Reaction(Metadata):
    type: Literal["emoji", "custom_emoji"]
    emoji: str
    count: int
