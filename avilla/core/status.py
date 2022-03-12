from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class PartStatus:
    available: bool
    description: str

    unknown: bool = False


@dataclass
class Status:
    parts: Dict[str, PartStatus]

    @property
    def main(self) -> PartStatus:
        return self.parts["main"]

    def __init__(self, parts: Optional[List[str]] = None):
        self.parts = {}
        if parts:
            for part in parts:
                self.parts[part] = PartStatus(False, "", True)
        self.parts["main"] = PartStatus(False, "", True)

    def __getitem__(self, key: str) -> PartStatus:
        return self.parts[key]
