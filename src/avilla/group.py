from dataclasses import dataclass

from pydantic import BaseModel

from avilla.builtins.profile import GroupProfile


class Group(BaseModel):
    def __init__(self, id: str, profile: GroupProfile):
        super().__init__(id=id, profile=profile)

    id: str
    profile: GroupProfile


@dataclass
class GroupPtr:
    id: str
