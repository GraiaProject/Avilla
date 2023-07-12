from typing import TYPE_CHECKING, Any, ChainMap, Protocol, TypeVar

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


class SupportsArtifacts(Protocol):
    def get_staff_artifacts(self) -> ChainMap[Any, Any]:
        ...


class SupportsComponent(Protocol):
    def get_staff_components(self) -> dict[str, SupportsArtifacts]:
        ...


class SupportsStaff(SupportsArtifacts, SupportsComponent, Protocol):
    ...
