from avilla.builtins.profile import GroupProfile
from avilla.group import Group
from avilla.profile import BaseProfile
from pydantic import BaseModel


class AnonymousProfile(BaseModel, BaseProfile):
    id: str
    name: str
    group: Group[GroupProfile]

    _internal_id: str = None
