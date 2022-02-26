from dataclasses import dataclass
from typing import Dict

@dataclass
class PartStatus:
    available: bool
    description: str

@dataclass
class Status:
    parts: Dict[str, PartStatus]

    available: bool
    description: str