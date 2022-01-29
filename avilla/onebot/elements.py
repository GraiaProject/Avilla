from dataclasses import dataclass

from avilla.core.message import Element


@dataclass
class Reply(Element):
    id: str
