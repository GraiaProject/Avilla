from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generator,
    Protocol,
    TypeVar,
)

from typing_extensions import ParamSpec, TypeAlias

if TYPE_CHECKING:
    from ryanvk.collector import BaseCollector
    from ryanvk.fn.record import FnOverloadHarvest

T = TypeVar("T")
R = TypeVar("R", covariant=True)
P = ParamSpec("P")

unspecifiedCollectP = ParamSpec("unspecifiedCollectP")
specifiedCollectP = ParamSpec("specifiedCollectP")

inRC = TypeVar("inRC", covariant=True, bound=Callable)
inTC = TypeVar("inTC", bound=Callable)


class SupportsCollect(Protocol[P, R]):
    def collect(self, collector: Any, *args: P.args, **kwargs: P.kwargs) -> R:
        ...


class ImplementForCollect(Protocol[unspecifiedCollectP]):
    def collect(self, *args: unspecifiedCollectP.args, **kwargs: unspecifiedCollectP.kwargs) -> Any:
        ...


Twin: TypeAlias = "tuple[BaseCollector, Any]"

FnComposeCollectReturnType = Generator["FnOverloadHarvest", Any, None]
FnComposeCallReturnType = Generator["FnOverloadHarvest", None, R]
