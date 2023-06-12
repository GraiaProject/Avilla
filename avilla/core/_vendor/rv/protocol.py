from typing import TYPE_CHECKING, Callable, ClassVar, TypeVar, Protocol, Any
from typing_extensions import ParamSpec, Self

if TYPE_CHECKING:
    from .collect import Collector
    from .runner import Runner

P = ParamSpec("P")
C = TypeVar("C", contravariant=True, bound="Collector")
N = TypeVar("N", contravariant=True, bound="Runner")
R = TypeVar("R", covariant=True)
T = TypeVar("T")


class SupportsCollect(Protocol[C, P, R]):
    def collect(self, collector: C, *args: P.args, **kwargs: P.kwargs) -> R:
        ...

class Ring3(Protocol):
    __collector__: ClassVar[Collector]


class Executable(Protocol[N, P, R]):
    def execute(self, runner: N, *args: P.args, **kwargs: P.kwargs) -> R:
        ...