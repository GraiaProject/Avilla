from __future__ import annotations

import inspect
from functools import partial
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Final,
    Generic,
    Literal,
    NoReturn,
    Protocol,
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


UnboundSelector: Final = Selector()
TBounded = TypeVar("TBounded", bound=bool)


class Trait(Generic[TBounded]):
    context: Context
    bound: Selector | MetadataOf

    def __init__(self, context: Context, bound: Selector | MetadataOf) -> None:
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

_P2 = ParamSpec("_P2")
_T1_co = TypeVar("_T1_co", covariant=True)
_T2_co = TypeVar("_T2_co", covariant=True)


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
    def __get__(self, instance: Any, owner: type) -> Self:
        ...

    def __get__(self, instance: ..., owner: ...) -> Self | FnCall[_P, _T]:
        if not isinstance(instance, Trait):
            return self
        if instance.bound is UnboundSelector:
            raise RuntimeError(f"{self!r} cannot be called in a unbounded context")
        return BoundedFnCall(instance, self)

    @classmethod
    def bound(cls, schema: Callable[Concatenate[_TboundTrait, _P1], Awaitable[_T1]]) -> BoundFn[_P1, _T1]:
        return BoundFn(schema)

    @classmethod
    def bound_overload(
        cls, schema: type[OverrideSchema[_P, _T1_co, _P2, _T2_co]]
    ) -> OverrideFn[_P, _T1_co, _P2, _T2_co]:
        return OverrideFn(schema)


class FnCall(Generic[_P, _T]):
    trait: Trait
    fn: Fn[_P, _T]

    def __init__(self, trait: Trait, fn: Fn[_P, _T]):
        self.trait = trait
        self.fn = fn

    def __repr__(self) -> str:
        return f"<FnCall async {identity(self.trait)}::{self.fn.identity} {inspect.signature(self.fn.schema)}>"

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs):
        bounding = (
            self.trait.bound.path_without_land
            if isinstance(self.trait.bound, Selector)
            else self.trait.bound.to_bounding()
        )
        impl = self.trait.context._artifacts.get(Bounds(bounding), {}).get(Impl(self.fn))
        if impl is None:
            raise NotImplementedError(
                f'"{identity(self.trait)}::{self.fn.identity}" '
                f'in "{identity(self.trait.context.protocol)}" '
                "is not implemented."
            )
        impl = cast("Callable[Concatenate[Context, _P], Awaitable[_T]]", impl)
        return await impl(self.trait.context, *args, **kwargs)


# TODO: UnboundTrait, UnboundFn
class BoundFn(Fn[_P, _T]):
    @overload
    def __init__(self, schema: Callable[Concatenate[_TboundTrait, _P], Awaitable[_T]]):
        ...

    @overload
    def __init__(self, schema: Callable[_P, Awaitable[_T]]):
        ...

    def __init__(self, schema: ...):
        self.schema = schema

    def __repr__(self) -> str:
        return f"<Fn bound-required async {self.trait.__name__}::{self.identity} {inspect.signature(self.schema)}>"

    @overload
    def __get__(self, instance: Trait[Literal[True]], owner: type[Trait]) -> BoundedFnCall[_P, _T]:
        ...

    @overload
    def __get__(self, instance: Trait[Literal[False]], owner: type[Trait]) -> UnboundedFnCall[_P, _T]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type) -> Self:
        ...

    def __get__(self, instance: ..., owner: ...) -> Self | FnCall:
        if isinstance(instance, Trait):
            if instance.bound is UnboundSelector:
                return UnboundedFnCall(instance, self)
            else:
                return BoundedFnCall(instance, self)
        return self


class BoundedFnCall(FnCall[_P, _T]):
    def __repr__(self) -> str:
        return f"<FnCall bounded async {self.trait.__class__.__name__}::{self.fn.identity} {inspect.signature(self.fn.schema)}>"

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs):
        bounding = (
            self.trait.bound.path_without_land
            if isinstance(self.trait.bound, Selector)
            else self.trait.bound.to_bounding()
        )
        impl = self.trait.context._artifacts.get(Bounds(bounding), {}).get(Impl(self.fn))
        if impl is None:
            raise NotImplementedError(
                f'"{identity(self.trait)}::{self.fn.identity}" '
                f'in "{identity(self.trait.context.protocol)}" '
                f'for target "{bounding}" '
                "is not implemented."
            )
        impl = cast("Callable[Concatenate[Context, Selector | MetadataOf, _P], Awaitable[_T]]", impl)
        return await impl(self.trait.context, self.trait.bound, *args, **kwargs)


class UnboundedFnCall(FnCall[_P, _T]):
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


class OverrideSchema(Protocol[_P, _T1_co, _P2, _T2_co]):
    async def bound(self, *args: _P.args, **kwargs: _P.kwargs) -> _T1_co:
        ...

    async def unbound(self, *args: _P2.args, **kwargs: _P2.kwargs) -> _T2_co:
        ...


class OverrideFn(BoundFn, Generic[_P, _T1_co, _P2, _T2_co]):
    trait: type[Trait]
    identity: str
    schema: type[OverrideSchema[_P, _T1_co, _P2, _T2_co]]

    def __init__(self, schema: type[OverrideSchema[_P, _T1_co, _P2, _T2_co]]):
        self.schema = schema

    def __set_name__(self, owner: type[Trait], attr: str):
        self.trait = owner
        self.identity = attr

    def __repr__(self) -> str:
        return (
            f"<OverrideFn async {self.trait.__name__}::{self.identity} "
            f"bound#[{inspect.signature(partial(self.schema.bound, NoReturn))}] "
            f"unbound#[{inspect.signature(partial(self.schema.unbound, NoReturn))}]>"
        )

    @overload
    def __get__(self, instance: Trait[Literal[True]], owner: type[Trait]) -> BoundedFnCall[_P, _T1_co]:
        ...

    @overload
    def __get__(self, instance: Trait[Literal[False]], owner: type[Trait]) -> UnboundedFnCall[_P2, _T2_co]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type) -> Self:
        ...

    def __get__(self, instance: ..., owner: ...):
        if isinstance(instance, Trait):
            if instance.bound is UnboundSelector:
                return UnboundedFnCall(instance, self)
            else:
                return BoundedFnCall(instance, self)
        return self
