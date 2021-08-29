from typing import Optional

from avilla.core.group import Group
from avilla.core.profile import BaseProfile
from pydantic import BaseModel  # pylint: ignore


class AnonymousProfile(BaseModel, BaseProfile):
    id: str
    name: str
    group: Group

    _internal_id: Optional[str] = None
