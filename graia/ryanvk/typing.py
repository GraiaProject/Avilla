from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Generic, Protocol

from typing_extensions import Concatenate, ParamSpec, TypeVar

from graia.ryanvk.aio import queue_task

if TYPE_CHECKING:
    from .collector import BaseCollector  # noqa
    from .staff import Staff

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

