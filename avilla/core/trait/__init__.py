from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from functools import partial
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast, overload

from typing_extensions import Concatenate, ParamSpec, Self

from avilla.core.selector import Selector
from avilla.core.utilles import identity

from ..metadata import MetadataOf
from .signature import Bounds, Impl

if TYPE_CHECKING:
    from avilla.core.context import Context


_P = ParamSpec("_P")
_T = TypeVar("_T")

_P1 = ParamSpec("_P1")
_T1 = TypeVar("_T1")

_TboundTrait = TypeVar("_TboundTrait", bound="Trait")


class Trait:
    context: Context
    bound: Selector | MetadataOf

    def __init__(self, context: Context, bound: Selector | MetadataOf) -> None:
        self.context = context
        self.bound = bound

    @classmethod
    def fn(cls) -> list[Fn]:
        return [fn for _, fn in inspect.getmembers(cls, lambda a: isinstance(a, Fn))]


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
        return FnCall(instance, self) if issubclass(owner, Trait) else self

    @classmethod
    def configure(cls, **kwargs):
        return partial(cls.__new__, **kwargs)

    @classmethod
    def bound_entity(cls, schema: Callable[Concatenate[_TboundTrait, _P1], Awaitable[_T1]]) -> BoundEntityFn[_P1, _T1]:
        return BoundEntityFn(schema)

    @classmethod
    def bound_metadata(
        cls, schema: Callable[Concatenate[_TboundTrait, _P1], Awaitable[_T1]]
    ) -> BoundMetadataFn[_P1, _T1]:
        return BoundMetadataFn(schema)

    @classmethod
    def bound_universal(
        cls, schema: Callable[Concatenate[_TboundTrait, _P1], Awaitable[_T1]]
    ) -> BoundUniversalFn[_P1, _T1]:
        return BoundUniversalFn(schema)


class FnCall(Generic[_P, _T]):
    trait: Trait
    fn: Fn[_P, _T]

    def __init__(self, trait: Trait, fn: Fn[_P, _T]):
        self.trait = trait
        self.fn = fn

    def __repr__(self) -> str:
        return f"<FnCall async {identity(self.trait)}::{self.fn.identity} {inspect.signature(self.fn.schema)}>"

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs):
        impl = self.trait.context._impl_artifacts.get(Impl(self.fn))
        if impl is None:
            raise NotImplementedError(
                f'"{identity(self.trait)}::{self.fn.identity}" '
                f'in "{identity(self.trait.context.protocol)}" '
                "is not implemented."
            )
        impl = cast(Callable[Concatenate["Context", _P], Awaitable[_T]], impl)
        return await impl(self.trait.context, *args, **kwargs)


class BoundFnCommon(Fn[_P, _T]):
    @overload
    def __init__(self, schema: Callable[Concatenate[_TboundTrait, _P], Awaitable[_T]]):
        ...

    @overload
    def __init__(self, schema: Callable[_P, Awaitable[_T]]):
        ...

    def __init__(self, schema: Any):
        self.schema = schema


class BoundEntityFn(BoundFnCommon[_P, _T]):
    def __repr__(self) -> str:
        return (
            f"<Fn bound-required entity async {self.trait.__name__}::{self.identity} {inspect.signature(self.schema)}>"
        )

    @overload
    def __get__(self, instance: Trait, owner: type[Trait]) -> AppliedEntityFnCall[_P, _T]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type[Trait]) -> UnappliedEntityFnCall[_P, _T]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type) -> Self:
        ...

    def __get__(self, instance: Any, owner: type):
        if issubclass(owner, Trait):
            if isinstance(instance, Trait):
                return AppliedEntityFnCall(instance, self)
            return UnappliedEntityFnCall(instance, self)
        return self


class BoundMetadataFn(BoundFnCommon[_P, _T]):
    def __repr__(self) -> str:
        return f"<Fn bound-required metadata async {self.trait.__name__}::{self.identity} {inspect.signature(self.schema)}>"

    @overload
    def __get__(self, instance: Trait, owner: type[Trait]) -> AppliedMetadataFnCall[_P, _T]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type[Trait]) -> UnappliedMetadataFnCall[_P, _T]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type) -> Self:
        ...

    def __get__(self, instance: Any, owner: type):
        if issubclass(owner, Trait):
            if isinstance(instance, Trait):
                return AppliedMetadataFnCall(instance, self)
            return UnappliedMetadataFnCall(instance, self)
        return self


class BoundUniversalFn(BoundFnCommon[_P, _T]):
    def __repr__(self) -> str:
        return f"<Fn bound-required universal async {self.trait.__name__}::{self.identity} {inspect.signature(self.schema)}>"

    @overload
    def __get__(self, instance: Trait, owner: type[Trait]) -> AppliedUniversalFnCall[_P, _T]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type[Trait]) -> UnappliedUniversalFnCall[_P, _T]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type) -> Self:
        ...

    def __get__(self, instance: Any, owner: type):
        if issubclass(owner, Trait):
            if isinstance(instance, Trait):
                return AppliedUniversalFnCall(instance, self)
            return UnappliedUniversalFnCall(instance, self)
        return self


class UnappliedEntityFnCall(FnCall[_P, _T]):
    def __repr__(self) -> str:
        return f"<FnCall unbounded entity async {self.trait.__class__.__name__}::{self.fn.identity} {inspect.signature(self.fn.schema)}>"

    async def __call__(self, target: Selector, *args: _P.args, **kwargs: _P.kwargs):
        impl = self.trait.context._get_entity_bound_scope(target).get(Impl(self.fn))
        if impl is None:
            raise NotImplementedError(
                f'"{identity(self.trait)}::{self.fn.identity}" for target "{target!r}" is not implemented.'
            )
        impl = cast(Callable[Concatenate["Context", Selector, _P], Awaitable[_T]], impl)
        return await impl(self.trait.context, target, *args, **kwargs)


class UnappliedMetadataFnCall(FnCall[_P, _T]):
    def __repr__(self) -> str:
        return f"<FnCall unbounded metadata async {self.trait.__class__.__name__}::{self.fn.identity} {inspect.signature(self.fn.schema)}>"

    async def __call__(self, target: MetadataOf, *args: _P.args, **kwargs: _P.kwargs):
        impl = self.trait.context._get_metadata_bound_scope(target).get(Impl(self.fn))
        if impl is None:
            raise NotImplementedError(
                f'"{identity(self.trait)}::{self.fn.identity}" for target "{target!r}" is not implemented.'
            )
        impl = cast(Callable[Concatenate["Context", MetadataOf, _P], Awaitable[_T]], impl)
        return await impl(self.trait.context, target, *args, **kwargs)


class UnappliedUniversalFnCall(FnCall[_P, _T]):
    def __repr__(self) -> str:
        return f"<FnCall unbounded universal async {self.trait.__class__.__name__}::{self.fn.identity} {inspect.signature(self.fn.schema)}>"

    async def __call__(self, target: Selector | MetadataOf, *args: _P.args, **kwargs: _P.kwargs):
        if isinstance(target, Selector):
            scope = self.trait.context._get_entity_bound_scope(target)
        else:
            scope = self.trait.context._get_metadata_bound_scope(target)
        impl = scope.get(Impl(self.fn))
        if impl is None:
            raise NotImplementedError(
                f'"{identity(self.trait)}::{self.fn.identity}" for target "{target!r}" is not implemented.'
            )
        impl = cast(Callable[Concatenate["Context", "Selector | MetadataOf", _P], Awaitable[_T]], impl)
        return await impl(self.trait.context, target, *args, **kwargs)

    def assert_entity(self, target: Selector | MetadataOf):
        if not isinstance(target, Selector):
            raise TypeError(f'"{identity(self.trait)}::{self.fn.identity}" expected bounds with a entity.')

    def assert_metadata(self, target: Selector | MetadataOf):
        if not isinstance(target, MetadataOf):
            raise TypeError(f'"{identity(self.trait)}::{self.fn.identity}" expected bounds with a metadata referring.')


class AppliedEntityFnCall(FnCall[_P, _T]):
    def __repr__(self) -> str:
        return f"<FnCall bounded entity async {self.trait.__class__.__name__}::{self.fn.identity} {inspect.signature(self.fn.schema)}>"

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs):
        target = self.trait.bound
        if not isinstance(target, Selector):
            raise TypeError(f'"{identity(self.trait)}::{self.fn.identity}" expected bounds with a entity.')
        impl = self.trait.context._get_entity_bound_scope(target).get(Impl(self.fn))
        if impl is None:
            raise NotImplementedError(
                f'"{identity(self.trait)}::{self.fn.identity}" for target "{target!r}" is not implemented.'
            )
        impl = cast(Callable[Concatenate["Context", Selector, _P], Awaitable[_T]], impl)
        return await impl(self.trait.context, target, *args, **kwargs)


class AppliedMetadataFnCall(FnCall[_P, _T]):
    def __repr__(self) -> str:
        return f"<FnCall bounded metadata async {self.trait.__class__.__name__}::{self.fn.identity} {inspect.signature(self.fn.schema)}>"

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs):
        target = self.trait.bound
        if not isinstance(target, MetadataOf):
            raise TypeError(f'"{identity(self.trait)}::{self.fn.identity}" expected bounds with a metadata referring.')
        impl = self.trait.context._get_metadata_bound_scope(target).get(Impl(self.fn))
        if impl is None:
            raise NotImplementedError(
                f'"{identity(self.trait)}::{self.fn.identity}" for target "{target!r}" is not implemented.'
            )
        impl = cast(Callable[Concatenate["Context", MetadataOf, _P], Awaitable[_T]], impl)
        return await impl(self.trait.context, target, *args, **kwargs)


class AppliedUniversalFnCall(FnCall[_P, _T]):
    def __repr__(self) -> str:
        return f"<FnCall bounded universal async {self.trait.__class__.__name__}::{self.fn.identity} {inspect.signature(self.fn.schema)}>"

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs):
        target = self.trait.bound
        if isinstance(target, Selector):
            scope = self.trait.context._get_entity_bound_scope(target)
        else:
            scope = self.trait.context._get_metadata_bound_scope(target)
        impl = scope.get(Impl(self.fn))
        if impl is None:
            raise NotImplementedError(
                f'"{identity(self.trait)}::{self.fn.identity}" for target "{target!r}" is not implemented.'
            )
        impl = cast(Callable[Concatenate["Context", "Selector | MetadataOf", _P], Awaitable[_T]], impl)
        return await impl(self.trait.context, target, *args, **kwargs)
