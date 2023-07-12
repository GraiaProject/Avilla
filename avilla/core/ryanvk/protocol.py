from typing import TYPE_CHECKING, Protocol, TypeVar, Any

from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from .collector.base import BaseCollector

P = ParamSpec("P")
C = TypeVar("C", contravariant=True, bound="BaseCollector")
C1 = TypeVar("C1", bound="BaseCollector")
R = TypeVar("R", covariant=True)
T = TypeVar("T")


class SupportsCollect(Protocol[C, P, R]):
    def collect(self, collector: C, *args: P.args, **kwargs: P.kwargs) -> R:
        ...

class SupportsComponent(Protocol):
    def get_ryanvk_components(self) -> dict[str, Any]:
        ...
