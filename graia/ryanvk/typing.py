from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, Protocol, Union, runtime_checkable

from typing_extensions import ParamSpec, TypeVar

if TYPE_CHECKING:
    from .collector import BaseCollector  # noqa

P = ParamSpec("P")
P1 = ParamSpec("P1")
R = TypeVar("R", infer_variance=True)
T = TypeVar("T")
C = TypeVar("C", bound="BaseCollector")
CQ = TypeVar("CQ", bound="BaseCollector")


class SupportsCollect(Protocol[P, R]):
    def collect(self, collector: Any, *args: P.args, **kwargs: P.kwargs) -> R:  # type: ignore
        ...


R1 = TypeVar("R1", covariant=True)
R2 = TypeVar("R2", covariant=True)


@dataclass(frozen=True, eq=True)
class Twin(Generic[R1, R2]):
    _0: R1
    _1: R2


class ClsIncluded(Protocol[T]):
    cls: type[T]


Cr = TypeVar("Cr", bound="BaseCollector", covariant=True)


@runtime_checkable
class SupportsMerge(Protocol):
    def merge(self, *records: dict):
        ...


class LayoutProtocolProperty(Protocol):
    @property
    def get_artifact_layout(self) -> dict:
        ...


class LayoutProtocolAttr(Protocol):
    get_artifact_layout: dict


LayoutProtocol = Union[LayoutProtocolProperty, LayoutProtocolAttr]
