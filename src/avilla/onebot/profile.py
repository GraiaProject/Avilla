from typing import Optional
from pydantic import BaseModel  # pylint: ignore

from avilla.builtins.profile import GroupProfile
from avilla.group import Group
from avilla.profile import BaseProfile


class AnonymousProfile(BaseModel, BaseProfile):
    id: str
    name: str
    group: Group[GroupProfile]

    _internal_id: Optional[str] = None
