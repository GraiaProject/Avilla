from dataclasses import dataclass

from avilla.core.event import RelationshipCreated, RelationshipDestroyed


@dataclass
class RoleCreated(RelationshipCreated):
    ...


@dataclass
class RoleDestroyed(RelationshipDestroyed):
    ...
