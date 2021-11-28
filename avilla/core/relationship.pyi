from datetime import timedelta
from typing import Any, List, TypeVar, Union, overload

from avilla.core.execution import Execution as Execution
from avilla.core.execution import Result
from avilla.core.metadata import Metadata as Metadata
from avilla.core.protocol import BaseProtocol as BaseProtocol
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import rsctx as rsctx
from avilla.core.selectors import self as self_selector
from avilla.core.typing import T_ExecMW, T_Profile

class ExecutorWrapper:
    relationship: "Relationship"
    execution: Execution
    middlewares: List[T_ExecMW]
    def __init__(self, relationship: "Relationship") -> None: ...
    def __await__(self): ...
    def execute(self, execution: Execution): ...
    __call__: Any
    def to(self, target: Union[rsctx, mainline_selector]): ...
    def period(self, period: timedelta): ...
    def use(self, middleware: T_ExecMW): ...

T = TypeVar("T")

class Relationship:
    ctx: rsctx
    mainline: mainline_selector
    metadata: Metadata
    self: self_selector
    protocol: BaseProtocol
    def __init__(
        self,
        protocol: BaseProtocol,
        ctx: rsctx,
        current_self: self_selector,
        middlewares: List[T_ExecMW] = ...,
    ) -> None: ...
    @property
    def current(self) -> self_selector: ...
    def has_ability(self, ability: str) -> bool: ...
    @overload
    async def exec(self, execution: Execution) -> Any: ...
    @overload
    async def exec(self, execution: Result[T]) -> T: ...
