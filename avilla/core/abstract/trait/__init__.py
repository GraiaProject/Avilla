from __future__ import annotations
from functools import partial

import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generic,
    TypeVar,
    cast,
    overload,
)

from typing_extensions import Concatenate, ParamSpec, Self

from avilla.core.utilles import identity
from avilla.core.utilles.selector import Selector

from ..metadata import MetadataOf
from .signature import Bounds, Impl

if TYPE_CHECKING:
    from avilla.core.context import Context


class Trait:
    context: Context
    bound: Selector

    def __init__(self, context: Context, bound: Selector) -> None:
        self.context = context
        self.bound = bound

    @classmethod
    def fn(cls) -> list[Fn]:
        return [fn for _, fn in inspect.getmembers(cls, lambda a: isinstance(a, Fn))]


_P = ParamSpec("_P")
_T = TypeVar("_T")

_P1 = ParamSpec("_P1")
_T1 = TypeVar("_T1")

_TboundTrait = TypeVar("_TboundTrait", bound=Trait)


class Fn(Generic[_P, _T]):
    trait: type[Trait]
    identity: str
    schema: Callable[_P, Awaitable[_T]]

    def __init__(self, schema: Callable[_P, Awaitable[_T]]):
        self.schema = schema

    def __set_name__(self, owner: type[Trait], attr: str):
        self.trait = owner
        self.identity = attr

    def __repr__(self) -> str:
        return f"<Fn async {self.trait.__name__}::{self.identity} {inspect.signature(self.schema)}>"

    @overload
    def __get__(self, instance: Trait, owner: type[Trait]) -> FnCall[_P, _T]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type[Trait]) -> FnCall[_P, _T]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type) -> Self:
        ...

    def __get__(self, instance: Any, owner: type) -> Self | FnCall[_P, _T]:
        if issubclass(owner, Trait):
            return FnCall(instance, self)
        return self

    @classmethod
    def configure(cls, **kwargs):
        return partial(cls.__new__, **kwargs)

    @classmethod
    def bound(cls, schema: Callable[Concatenate[_TboundTrait, _P1], Awaitable[_T1]]) -> BoundFn[_P1, _T1]:
        return BoundFn(schema)


class FnCall(Generic[_P, _T]):
    trait: Trait
    fn: Fn[_P, _T]

    def __init__(self, trait: Trait, fn: Fn[_P, _T]):
        self.trait = trait
        self.fn = fn

    def __repr__(self) -> str:
        return f"<FnCall async {identity(self.trait)}::{self.fn.identity} {inspect.signature(self.fn.schema)}>"

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs):
        impl = self.trait.context._artifacts.get(Impl(self.fn))
        if impl is None:
            raise NotImplementedError(
                f'"{identity(self.trait)}::{self.fn.identity}" '
                f'in "{identity(self.trait.context.protocol)}" '
                "is not implemented."
            )
        impl = cast("Callable[Concatenate[Context, _P], Awaitable[_T]]", impl)
        return await impl(self.trait.context, *args, **kwargs)


class BoundFn(Fn[_P, _T]):
    @overload
    def __init__(self, schema: Callable[Concatenate[_TboundTrait, _P], Awaitable[_T]]):
        ...

    @overload
    def __init__(self, schema: Callable[_P, Awaitable[_T]]):
        ...

    def __init__(self, schema: Any):
        self.schema = schema

    def __repr__(self) -> str:
        return f"<Fn bound-required async {self.trait.__name__}::{self.identity} {inspect.signature(self.schema)}>"

    @overload
    def __get__(self, instance: Trait, owner: type[Trait]) -> AppliedFnCall[_P, _T]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type[Trait]) -> UnappliedFnCall[_P, _T]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type) -> Self:
        ...

    def __get__(self, instance: Any, owner: type) -> Self | UnappliedFnCall | AppliedFnCall:
        if issubclass(owner, Trait):
            if isinstance(instance, Trait):
                return UnappliedFnCall(instance, self)
            return AppliedFnCall(instance, self)
        return self



class UnappliedFnCall(FnCall[_P, _T]):
    def __repr__(self) -> str:
        return f"<FnCall unbounded async {self.trait.__class__.__name__}::{self.fn.identity} {inspect.signature(self.fn.schema)}>"

    async def __call__(self, target: Selector | MetadataOf, *args: _P.args, **kwargs: _P.kwargs):
        bounding = target.path_without_land if isinstance(target, Selector) else target.to_bounding()
        impl = self.trait.context._artifacts.get(Bounds(bounding), {}).get(
            Impl(self.fn)
        )  # TODO: Signature for Fn refactor
        if impl is None:
            raise NotImplementedError(
                f'"{identity(self.trait)}::{self.fn.identity}" ' f'for target "{bounding}" ' "is not implemented."
            )
        impl = cast("Callable[Concatenate[Context, Selector | MetadataOf, _P], Awaitable[_T]]", impl)
        return await impl(self.trait.context, target, *args, **kwargs)

class AppliedFnCall(FnCall[_P, _T]):
    def __repr__(self) -> str:
        return f"<FnCall unbounded async {self.trait.__class__.__name__}::{self.fn.identity} {inspect.signature(self.fn.schema)}>"

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs):
        target = self.trait.bound
        bounding = target.path_without_land if isinstance(target, Selector) else target.to_bounding()
        impl = self.trait.context._artifacts.get(Bounds(bounding), {}).get(
            Impl(self.fn)
        )  # TODO: Signature for Fn refactor
        if impl is None:
            raise NotImplementedError(
                f'"{identity(self.trait)}::{self.fn.identity}" ' f'for target "{bounding}" ' "is not implemented."
            )
        impl = cast("Callable[Concatenate[Context, Selector | MetadataOf, _P], Awaitable[_T]]", impl)
        return await impl(self.trait.context, target, *args, **kwargs)
