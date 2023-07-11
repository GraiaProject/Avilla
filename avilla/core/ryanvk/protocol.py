from typing import TYPE_CHECKING, Protocol, TypeVar

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


class Ring3(Protocol[C1]):
    __collector__: C1
