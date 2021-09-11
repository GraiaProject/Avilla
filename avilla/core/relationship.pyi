from avilla.core.contactable import Contactable
from typing import Any, Generic, Iterable, List, Optional, TypeVar, overload

from avilla.core.builtins.profile import SelfProfile
from avilla.core.execution import Execution, Result
from avilla.core.protocol import BaseProtocol
from avilla.core.typing import T_ExecMW, T_Profile

T = TypeVar("T")

class Relationship(Generic[T_Profile]):
    ctx: Contactable[T_Profile]
    protocol: BaseProtocol
    _middlewares: List[T_ExecMW]
    _self: Optional[Contactable[SelfProfile]]
    def __init__(
        self,
        ctx: Contactable[T_Profile],
        protocol: BaseProtocol,
        middlewares: List[T_ExecMW] = None,
    ) -> None: ...
    @property
    def current(self) -> Contactable: ...
    async def get_members(self) -> "Iterable[Contactable[T_Profile]]": ...
    @overload
    async def exec(self, execution: Execution, *user_middlewares: T_ExecMW) -> Any: ...
    @overload
    async def exec(self, execution: Result[T], *user_middlewares: T_ExecMW) -> T: ...
