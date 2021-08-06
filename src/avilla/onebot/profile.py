from typing import Optional

from pydantic import BaseModel  # pylint: ignore

from avilla.group import Group
from avilla.profile import BaseProfile


class AnonymousProfile(BaseModel, BaseProfile):
    id: str
    name: str
    group: Group

    _internal_id: Optional[str] = None
