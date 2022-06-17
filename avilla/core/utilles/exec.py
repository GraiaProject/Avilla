from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from avilla.core.execution import Execution

T = TypeVar("T")


class ExecutionHandler(Generic[T]):
    handlers: dict[type[Execution], Callable[[T, Execution], Awaitable[Any]]] = {}

    def __init_subclass__(cls, **kwargs):
        cls.handlers = {}
        for base in reversed(cls.__bases__):
            if issubclass(base, ExecutionHandler):
                cls.handlers.update(base.handlers)

    async def trig(self, protocol: T, execution: Execution) -> Any:
        handler = self.handlers.get(type(execution))
        if not handler:
            raise NotImplementedError(f"No handler for {type(execution)}")
        return await handler(protocol, execution)
