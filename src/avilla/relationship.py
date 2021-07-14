from dataclasses import dataclass
from typing import Any, Iterable, Generic, TYPE_CHECKING, Union, TypeVar

from avilla.entity import Entity
from avilla.execution import Execution, Result
from avilla.group import Group
from .region import Region

if TYPE_CHECKING:
    from .protocol import BaseProtocol

T_Profile = TypeVar("T_Profile")
T_Protocol = TypeVar("T_Protocol", "BaseProtocol", Any)
T_GroupProfile = TypeVar("T_GroupProfile")

@dataclass
class Relationship(Generic[T_Profile, T_GroupProfile, T_Protocol]):
    region: Region
    entity_or_group: Union[Entity[T_Profile], Group[T_Profile, T_GroupProfile]]
    protocol: T_Protocol

    @property
    def current(self) -> Union[Entity[T_Profile], Group[T_Profile, T_GroupProfile]]:
        return self.protocol.getSelf()
    
    async def getMembers(self) -> 'Iterable[Entity[T_Profile]]':
        if not isinstance(self.entity_or_group, Group):
            return [self.current, self.entity_or_group]
        return [self.current, *[i async for i in self.protocol.getMembers(self.entity_or_group) if i.id != self.current.id]]

    async def exec(self, execution: Execution) -> Any:
        return await self.protocol.ensureExecution(self, execution)
    
