from typing import Any, Awaitable, Callable, Dict, Generic, Optional, Tuple, TypeVar

from avilla.core.operator import Operator, OperatorCache

O = TypeVar("O", bound=Operator)


class OperatorImplementDispatch(Generic[O]):
    #                    key   op        operator value          cache
    patterns: Dict[Tuple[str, str], Callable[[O, Any, Optional[OperatorCache]], Awaitable[Any]]] = {}

    def __init_subclass__(cls, **kwargs) -> None:
        cls.patterns = {}
        for base in reversed(cls.__bases__):
            if issubclass(base, OperatorImplementDispatch):
                cls.patterns.update(base.patterns)

    async def operate(
        self, origin_op: O, op: str, target: str, value: Any, cache: Optional[OperatorCache] = None
    ) -> Any:
        operator = self.patterns.get((target, op))
        if not operator:
            raise KeyError(f"cannot dispatch for ({target}, {op})")
        return await operator(origin_op, value, cache)
