from typing import TYPE_CHECKING, Any, Callable, TypeVar
from typing_extensions import ParamSpec, Concatenate

from .common.fn import BaseFn


if TYPE_CHECKING:
    from .common.protocol import Ring3
    from .collector import Collector


P = ParamSpec("P")
T = TypeVar("T", covariant=True)

N = TypeVar("N", bound="Ring3")



class Fn(BaseFn[P, T]):
    def __init__(self, entity: Callable[Concatenate[N, P], T]) -> None:
        super().__init__()

class TargetFn(Fn[P, T]):
    def __init__(self, entity: Callable[Concatenate[N, P], T]) -> None:
        super().__init__(entity)

    def collect(self, collector: Collector, target: str):
        def receive(entity: Callable[Concatenate[N, P], T]):
            ...
        return receive
