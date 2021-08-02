from typing import Any, Generic, Iterable, Union, overload

from avilla.entity import Entity
from avilla.execution import Execution, Result
from avilla.group import Group
from avilla.typing import T_Protocol, T_GroupProfile, T_Profile, T_Result


class Relationship(Generic[T_Profile, T_GroupProfile, T_Protocol]):
    entity_or_group: Union[Entity[T_Profile], Group[T_GroupProfile]]
    protocol: T_Protocol

    def __init__(
        self, entity_or_group: Union[Entity[T_Profile], Group[T_GroupProfile]], protocol: T_Protocol
    ) -> None: ...
    @property
    def current(self) -> Union[Entity[T_Profile], Group[T_GroupProfile]]: ...
    async def get_members(self) -> "Iterable[Entity[T_Profile]]": ...
    @overload
    async def exec(self, execution: Execution) -> Any: ...
    @overload
    async def exec(self, execution: Result[T_Result]) -> T_Result: ...
    @overload
    async def exec(self, target: Union[Entity[T_Profile], Group, Any], execution: Execution) -> Any: ...

    @overload
    async def exec(
        self, target: Union[Entity[T_Profile], Group, Any], execution: Result[T_Result]
    ) -> T_Result: ...
