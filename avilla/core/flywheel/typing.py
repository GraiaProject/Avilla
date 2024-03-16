from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Protocol, TypeVar

from typing_extensions import Concatenate, ParamSpec

if TYPE_CHECKING:
    from .entity import BaseEntity
    from .fn.implement import FnImplementEntity


R = TypeVar("R", covariant=True)
R1 = TypeVar("R1", covariant=True)
P = ParamSpec("P")
P1 = ParamSpec("P1")
InP = ParamSpec("InP")
OutP = ParamSpec("OutP")
CR = TypeVar("CR", covariant=True, bound=Callable)
CT = TypeVar("CT", bound=Callable)
TEntity = TypeVar("TEntity", bound="BaseEntity")


class Collectable(Protocol[InP]):
    def collect(self, *args: InP.args, **kwargs: InP.kwargs) -> Any:
        ...


class Call(Protocol[P, R]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        ...


class AssignKeeper(Protocol[R]):
    def __call__(
        self: AssignKeeper[Call[..., Callable[P1, R1]]],
        implement: Callable[P1, R1] | FnImplementEntity[Callable[P1, R1]],
    ) -> FnImplementEntity[Callable[P1, R1]]:
        ...


class AssignKeeperCls(Protocol[R]):
    def __call__(
        self: AssignKeeperCls[Call[..., Callable[P1, R1]]],
        implement: Callable[Concatenate[Any, P1], R1] | FnImplementEntity[Callable[P1, R1]],
    ) -> FnImplementEntity[Callable[P1, R1]]:
        ...


class ImplementSample(Protocol[CR]):
    @property
    def implement_sample(self) -> CR:
        ...
