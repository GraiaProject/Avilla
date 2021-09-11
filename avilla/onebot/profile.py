from avilla.core.builtins.profile import GroupProfile
from avilla.core.contactable import Contactable
from typing import Optional

from avilla.core.profile import BaseProfile
from pydantic import BaseModel  # pylint: ignore


class AnonymousProfile(BaseModel, BaseProfile):
    id: str
    name: str
    group: Contactable[GroupProfile]

    _internal_id: Optional[str] = None
