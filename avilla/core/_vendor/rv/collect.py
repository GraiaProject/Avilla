from typing import TypeVar, Protocol, Any, final, NoReturn as Never
from typing_extensions import ParamSpec, Unpack, Self

P = ParamSpec("P")
C = TypeVar("C", contravariant=True, bound="Collector")
T = TypeVar("T", covariant=True)

class SupportsCollect(Protocol[C, P, T]):
    def collect(self, collector: C, *args: P.args, **kwargs: P.kwargs) -> T:
        ...

class Collector:
    artifacts: dict[Any, Any]

    def entity(self, signature: SupportsCollect[Self, P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        return signature.collect(self, *args, **kwargs)

    def _base_ring3(self):
        class collect_ring3:
            def __init_subclass__(cls) -> None:
                ...
        return collect_ring3
