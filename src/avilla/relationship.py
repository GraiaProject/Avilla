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

    def __init__(
        self, entity_or_group: Union[Entity[T_Profile], Group[T_GroupProfile]], protocol: T_Protocol
    ) -> None:
        self.entity_or_group = entity_or_group
        self.protocol = protocol

    @property
    def current(self) -> Union[Entity[T_Profile], Group[T_GroupProfile]]:
        return self.protocol.getSelf()

    @property
    def profile(self) -> Union[T_Profile, T_GroupProfile]:
        return self.entity_or_group.profile

    async def get_members(self) -> "Iterable[Entity[T_Profile]]":
        if not isinstance(self.entity_or_group, Group):
            return [self.current, self.entity_or_group]
        return [
            self.current,
            *[i for i in await self.protocol.get_members(self.entity_or_group) if i.id != self.current.id],
        ]

    async def exec(self, *args, **kwargs) -> Any:
        assert 0 < len(args) <= 2
        if len(args) == 1:
            execution = args[0]
        else:
            target, execution = args
            return await self.protocol.ensure_execution(
                relationship=self, execution=execution.with_target(target)
            )
        if kwargs.get("target"):
            target = kwargs["target"]
            return await self.protocol.ensure_execution(
                relationship=self, execution=execution.with_target(target)
            )
        else:
            return await self.protocol.ensure_execution(
                relationship=self, execution=execution.with_target(self.entity_or_group)
            )
