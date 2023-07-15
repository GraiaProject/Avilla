from typing import TYPE_CHECKING, Any, ChainMap, Protocol

from typing_extensions import ParamSpec, TypeVar

if TYPE_CHECKING:
    from .collector.base import BaseCollector

P = ParamSpec("P")
C = TypeVar("C", contravariant=True, bound="BaseCollector")
C1 = TypeVar("C1", bound="BaseCollector")
R = TypeVar("R", covariant=True)
T = TypeVar("T")

VnEventRaw = TypeVar("VnEventRaw", default=dict, infer_variance=True)
VnElementRaw = TypeVar("VnElementRaw", default=dict, infer_variance=True)


class SupportsCollect(Protocol[C, P, R]):
    def collect(self, collector: C, *args: P.args, **kwargs: P.kwargs) -> R:
        ...


class SupportsArtifacts(Protocol):
    def get_staff_artifacts(self) -> ChainMap[Any, Any]:
        ...


class SupportsComponent(Protocol):
    def get_staff_components(self) -> dict[str, SupportsArtifacts]:
        ...


class SupportsStaff(SupportsArtifacts, SupportsComponent, Protocol[VnElementRaw, VnEventRaw]):
    def __staff_generic__(self, element_type: VnElementRaw, event_type: VnEventRaw):
        ...
