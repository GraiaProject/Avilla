from typing import (Any, Generic, Iterable, List, Optional, TypeVar, Union,
                    overload)

from avilla.core.builtins.profile import SelfProfile
from avilla.core.entity import Entity
from avilla.core.execution import Execution, Result
from avilla.core.group import Group
from avilla.core.protocol import BaseProtocol
from avilla.core.typing import T_Ctx, T_ExecMW, T_Profile

T = TypeVar("T")

class Relationship(Generic[T_Ctx]):
    ctx: T_Ctx
    protocol: BaseProtocol
    _middlewares: List[T_ExecMW]
    _self: Optional[Entity[SelfProfile]]
    def __init__(
        self,
        ctx: Union[Entity[T_Profile], Group],
        protocol: BaseProtocol,
        middlewares: List[T_ExecMW] = None,
    ) -> None: ...
    @property
    def current(self) -> Union[Entity[T_Profile], Group]: ...
    async def get_members(self) -> "Iterable[Entity[T_Profile]]": ...
    @overload
    async def exec(self, execution: Execution, *user_middlewares: T_ExecMW) -> Any: ...
    @overload
    async def exec(self, execution: Result[T], *user_middlewares: T_ExecMW) -> T: ...
