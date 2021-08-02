from typing import Any, Generic, Iterable, Union
from avilla.builtins.profile import SelfProfile

from avilla.entity import Entity
from avilla.group import Group
from avilla.typing import T_Profile, T_GroupProfile, T_Protocol


class Relationship(Generic[T_Profile, T_GroupProfile, T_Protocol]):
    entity_or_group: Union[Entity[T_Profile], Group[T_GroupProfile]]
    protocol: T_Protocol

    def __init__(
        self, entity_or_group: Union[Entity[T_Profile], Group[T_GroupProfile]], protocol: T_Protocol
    ) -> None:
        self.entity_or_group = entity_or_group
        self.protocol = protocol

    @property
    def current(self) -> Entity[SelfProfile]:
        return self.protocol.get_self()

    @property
    def profile(self) -> Union[T_Profile, T_GroupProfile]:
        return self.entity_or_group.profile

    async def get_members(self) -> "Iterable[Entity]":
        if not isinstance(self.entity_or_group, Group):
            raise ValueError("target is not a Group.")
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
                relationship=self, execution=execution.with_target(target)  # type: ignore
            )
        if kwargs.get("target"):
            target = kwargs["target"]
            return await self.protocol.ensure_execution(
                relationship=self, execution=execution.with_target(target)  # type: ignore
            )
        else:
            return await self.protocol.ensure_execution(
                relationship=self, execution=execution.with_target(self.entity_or_group)  # type: ignore
            )
