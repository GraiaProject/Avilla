from datetime import datetime, timedelta
from typing import Any, Generic, List, Literal, TypeVar, Union, overload

from avilla.core.execution import Execution as Execution
from avilla.core.protocol import BaseProtocol as BaseProtocol
from avilla.core.selectors import entity as entity
from avilla.core.selectors import mainline
from avilla.core.selectors import self as self_selector
from avilla.core.typing import T_ExecMW as T_ExecMW

class ExecutorWrapper:
    relationship: "Relationship"
    execution: Execution
    middlewares: List[T_ExecMW]
    def __init__(self, relationship: "Relationship") -> None: ...
    def __await__(self): ...
    def execute(self, execution: Execution): ...
    __call__: Any
    def to(self, target: Union[entity, mainline]): ...
    def period(self, period: timedelta): ...
    def use(self, middleware: T_ExecMW): ...

class MetaWrapper:
    relationship: "Relationship"
    def __init__(self, relationship: "Relationship") -> None: ...
    async def get(self, metakey: str) -> Any: ...
    async def set(self, metakey: str, value: Any) -> None: ...
    async def reset(self, metakey: str) -> None: ...
    async def prev(self, metakey: str) -> Any: ...
    async def next(self, metakey: str) -> Any: ...
    async def push(self, metakey: str, value: Any) -> None: ...
    async def pop(self, metakey: str, index: int) -> Any: ...
    async def add(self, metakey: str, value: Any) -> None: ...
    async def remove(self, metakey: str, value: Any) -> None: ...

M = TypeVar("M", bound=MetaWrapper)

class Relationship(Generic[M]):
    ctx: entity
    mainline: mainline
    self: self_selector
    protocol: "BaseProtocol"
    _middlewares: List[T_ExecMW]
    def __init__(
        self,
        protocol: BaseProtocol,
        ctx: entity,
        current_self: self_selector,
        middlewares: List[T_ExecMW] = ...,
    ) -> None: ...
    @property
    def current(self) -> self_selector: ...
    @property
    def meta(self) -> M: ...
    @property
    def exec(self): ...
    def has_ability(self, ability: str) -> bool: ...

class CoreSupport(MetaWrapper):
    @overload
    async def get(self, metakey: Literal["mainline.name"]) -> str: ...
    @overload
    async def set(self, metakey: Literal["mainline.name"], value: str) -> None: ...
    @overload
    async def get(self, metakey: Literal["mainline.description"]) -> str: ...
    @overload
    async def set(self, metakey: Literal["mainline.description"], value: str) -> None: ...
    @overload
    async def reset(self, metakey: Literal["mainline.description"]) -> None: ...
    @overload
    async def get(self, metakey: Literal["mainline.max_count"]) -> int: ...
    @overload
    async def get(self, metakey: Literal["mainline.current_count"]) -> int: ...
    @overload
    async def get(self, metakey: Literal["member.name"]) -> str: ...
    @overload
    async def get(self, metakey: Literal["member.nickname"]) -> str: ...
    @overload
    async def set(self, metakey: Literal["member.nickname"], value: str) -> None: ...
    @overload
    async def get(self, metakey: Literal["member.budget"]) -> str: ...
    @overload
    async def set(self, metakey: Literal["member.budget"], value: str) -> None: ...
    @overload
    async def get(self, metakey: Literal["member.muted"]) -> bool: ...
    @overload
    async def get(self, metakey: Literal["member.mute_period"]) -> Union[datetime, None]: ...
    @overload
    async def get(self, metakey: Literal["member.joined_at"]) -> datetime: ...
    @overload
    async def get(self, metakey: Literal["member.last_active_at"]) -> datetime: ...
    @overload
    async def get(self, metakey: Literal["self.name"]) -> str: ...
    @overload
    async def set(self, metakey: Literal["self.name"], value: str) -> None: ...
    @overload
    async def get(self, metakey: Literal["self.nickname"]) -> str: ...
    @overload
    async def set(self, metakey: Literal["self.nickname"], value: str) -> None: ...
    @overload
    async def get(self, metakey: Literal["self.budget"]) -> str: ...
    @overload
    async def set(self, metakey: Literal["self.budget"], value: str) -> None: ...
    @overload
    async def reset(self, metakey: Literal["self.budget"]) -> bool: ...
    @overload
    async def get(self, metakey: Literal["self.muted"]) -> bool: ...
    @overload
    async def get(self, metakey: Literal["self.mute_period"]) -> Union[datetime, None]: ...
    @overload
    async def get(self, metakey: Literal["self.joined_at"]) -> datetime: ...
    @overload
    async def get(self, metakey: Literal["self.last_active_at"]) -> datetime: ...