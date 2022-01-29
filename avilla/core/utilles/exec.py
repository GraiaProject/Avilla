from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, Generic, Type, TypeVar

from avilla.core.execution import Execution

T = TypeVar("T")
E = TypeVar("E", bound=Execution)


class ExecutionHandler(Generic[T]):
    handlers: Dict[Type[Execution], Callable[[T, Execution], Awaitable[Any]]] = {}

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
