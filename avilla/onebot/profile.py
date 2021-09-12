from typing import Optional

from pydantic import BaseModel  # pylint: ignore

from avilla.core.builtins.profile import GroupProfile
from avilla.core.contactable import Contactable
from avilla.core.profile import BaseProfile


class AnonymousProfile(BaseModel, BaseProfile):
    id: str
    name: str
    group: Contactable[GroupProfile]

    _internal_id: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
