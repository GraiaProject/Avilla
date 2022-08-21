from __future__ import annotations

import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    ClassVar,
    Concatenate,
    Generic,
    ParamSpec,
    TypeVar,
    cast,
    overload,
)
import typing

from typing_extensions import Self

from avilla.core.utilles.selector import Selector

from ..cell import Cell, CellOf
from .signature import Impl, ImplDefaultTarget

if TYPE_CHECKING:
    from avilla.core.relationship import Relationship

T = TypeVar("T", bound="Trait")


def _eval_upper(exp: str):
    frame = sys._getframe(2)
    return eval(exp, frame.f_globals, frame.f_locals)


class TraitOf(Cell, Generic[T]):
    __trait_of__: type[T]

    def __init_subclass__(cls) -> None:
        for i in cls.__orig_bases__:  # type: ignore
            if typing.get_origin(i) is TraitOf:
                cls.__trait_of__ = typing.get_args(i)[0]
        return super().__init_subclass__()


class Trait:
    relationship: Relationship
    path: type[Cell] | CellOf | None
    target: Selector | None = None

    def __init__(
        self, relationship: Relationship, path: type[Cell] | CellOf | None = None, *, target: Selector | None = None
    ) -> None:
        self.relationship = relationship
        self.path = path
        self.target = target


_P = ParamSpec("_P")
_T = TypeVar("_T")

_P1 = ParamSpec("_P1")
_T1 = TypeVar("_T1")

_TboundTrait = TypeVar("_TboundTrait", bound=Trait)


class TraitCall(Generic[_P, _T]):
    __attr__: str
    schema: Callable[_P, Awaitable[_T]]

    def __init__(self):
        ...

    def __set_name__(self, owner: type[Trait], attr: str):
        print("???", owner, attr)
        self.__attr__ = attr

    @overload
    def __get__(self, instance: Trait, owner: type[Trait]) -> TraitCallWrapper[_P, _T]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type[Trait] | None) -> Self:
        ...

    def __get__(self, instance: ..., owner: ...) -> Self | TraitCallWrapper[_P, _T]:
        if not isinstance(instance, Trait):
            return self
        return TraitCallWrapper(instance, self)

    @overload
    def bound(self, schema: Callable[Concatenate[_TboundTrait, _P1], Awaitable[_T1]]) -> TraitCall[_P1, _T1]:
        ...

    @overload
    def bound(self, schema: Callable[_P1, Awaitable[_T1]]) -> TraitCall[_P1, _T1]:
        ...

    def bound(self, schema: ...) -> ...:
        self.schema = schema
        return self


class TraitCallWrapper(Generic[_P, _T]):
    trait: Trait
    # call: TraitCall[_P, _T]

    def __init__(self, trait: Trait, call: TraitCall[_P, _T]):
        self.trait = trait
        self.call = call

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _T:
        artifact_impl = self.trait.relationship._artifacts.get(
            Impl(
                self.call,
                self.trait.target.path_without_land if self.trait.target is not None else None,
                self.trait.path,
            )
        )
        if artifact_impl is None:
            raise NotImplementedError(
                f'"{self.trait.__class__.__name__}::{self.call.__attr__}" '
                f'in "{self.trait.relationship.protocol.__class__.__name__}" '
                + (f'for target "{self.trait.target.path_without_land}"' if self.trait.target is not None else "")
                + "is not implemented"
            )
        artifact_impl = cast("Callable[Concatenate[Relationship, _P], Awaitable[_T]]", artifact_impl)
        return await artifact_impl(self.trait.relationship, *args, **kwargs)


class TargetTraitCall(TraitCall[_P, _T]):
    @overload
    def __get__(self, instance: Trait, owner: type[Trait]) -> TargetTraitCallWrapper[_P, _T]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type[Trait] | None) -> Self:
        ...

    def __get__(self, instance: ..., owner: ...) -> ...:
        if instance is None:
            return self
        return TargetTraitCallWrapper(instance, self)

    @overload
    def bound(self, schema: Callable[Concatenate[_TboundTrait, _P1], Awaitable[_T1]]) -> TargetTraitCall[_P1, _T1]:
        ...

    @overload
    def bound(self, schema: Callable[_P1, Awaitable[_T1]]) -> TargetTraitCall[_P1, _T1]:
        ...

    def bound(self, schema: ...) -> ...:
        self.schema = schema
        return self


class TargetTraitCallWrapper(TraitCallWrapper[_P, _T]):
    _args: tuple[Any, ...] | None = None
    _kwargs: dict[str, Any] | None = None
    target: Selector | None = None

    def to(self, target: Selector):
        self.target = target
        return self

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs):
        self._args = args
        self._kwargs = kwargs
        return self

    def __await__(self):
        return self.__await_impl__().__await__()

    async def __await_impl__(self) -> _T:
        if self._args is None or self._kwargs is None:
            raise ValueError("cannot call without param in shape of schema")

        target = self.target or self.trait.target
        if target is None:
            targetter = self.trait.relationship._artifacts.get(ImplDefaultTarget(self.trait.path, self.call))
            if targetter is None:
                raise NotImplementedError(
                    f'"{self.trait.__class__.__name__}::{self.call.__attr__}" '
                    "required a target, but no target given and no default getter implemented."
                )
            targetter = cast("Callable[[Relationship], Selector]", targetter)
            target = targetter(self.trait.relationship)
        artifact_impl = self.trait.relationship._artifacts.get(
            Impl(
                self.call,
                target.path_without_land,
                self.trait.path,
            )
        )
        if artifact_impl is None:
            raise NotImplementedError(
                f'"{self.trait.__class__.__name__}::{self.call.__attr__}" '
                f'in "{self.trait.relationship.protocol.__class__.__name__}" '
                f'for target "{target.path_without_land}" '
                "is not implemented"
            )
        artifact_impl = cast("Callable[Concatenate[Relationship, Selector, _P], Awaitable[_T]]", artifact_impl)
        return await artifact_impl(self.trait.relationship, target, *self._args, **self._kwargs)  # type: ignore
