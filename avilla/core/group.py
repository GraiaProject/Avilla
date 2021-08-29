from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from avilla.core.builtins.profile import GroupProfile


class Group(BaseModel):
    def __init__(self, id: str, profile: "GroupProfile"):
        super().__init__(id=id, profile=profile)

    id: str
    profile: "GroupProfile"

    @classmethod
    def get_ability_id(cls) -> str:
        return "group"


@dataclass
class GroupPtr:
    id: str


from avilla.core.builtins.profile import GroupProfile  # noqa

Group.update_forward_refs(GroupProfile=GroupProfile)
