from typing import TYPE_CHECKING, Any, Generic, Iterable, TypeVar, Union, overload

from avilla.entity import Entity
from avilla.execution import Execution, Result
from avilla.group import Group

if TYPE_CHECKING:
    from .protocol import BaseProtocol

T_Profile = TypeVar("T_Profile")
T_Protocol = TypeVar("T_Protocol", "BaseProtocol", Any)
T_GroupProfile = TypeVar("T_GroupProfile")

T_Result = TypeVar("T_Result")

class Relationship(Generic[T_Profile, T_GroupProfile, T_Protocol]):
    entity_or_group: Union[Entity[T_Profile], Group[T_GroupProfile]]
    protocol: T_Protocol
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
