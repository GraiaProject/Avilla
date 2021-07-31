from typing import TYPE_CHECKING, Any, Generic, Iterable, TypeVar, Union


from avilla.entity import Entity
from avilla.execution import Execution, Result
from avilla.group import Group

if TYPE_CHECKING:
    from .protocol import BaseProtocol

T_Profile = TypeVar("T_Profile")
T_Protocol = TypeVar("T_Protocol", "BaseProtocol", Any)
T_GroupProfile = TypeVar("T_GroupProfile")


class Relationship(Generic[T_Profile, T_GroupProfile, T_Protocol]):
    entity_or_group: Union[Entity[T_Profile], Group[T_GroupProfile]]
    protocol: T_Protocol

    @property
    def current(self) -> Union[Entity[T_Profile], Group[T_GroupProfile]]:
        return self.protocol.getSelf()

    @property
    def profile(self) -> Union[T_Profile, T_GroupProfile]:
        return self.entity_or_group.profile

    async def getMembers(self) -> "Iterable[Entity[T_Profile]]":
        if not isinstance(self.entity_or_group, Group):
            return [self.current, self.entity_or_group]
        return [
            self.current,
            *[i for i in await self.protocol.getMembers(self.entity_or_group) if i.id != self.current.id],
        ]

    async def exec(self, execution: Execution) -> Any:
        return await self.protocol.ensureExecution(relationship=self, execution=execution)
