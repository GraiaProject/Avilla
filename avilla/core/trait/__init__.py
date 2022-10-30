from __future__ import annotations

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

from ..cell import Cell, CellOf
from .signature import Impl, ImplDefaultTarget

if TYPE_CHECKING:
    from avilla.core.relationship import Context

from devtools import debug


class Trait:
    relationship: Context
    path: type[Cell] | CellOf | None
    target: Selector | None = None

    def __init__(
        self, relationship: Context, path: type[Cell] | CellOf | None = None, target: Selector | None = None
    ) -> None:
        self.relationship = relationship
        self.path = path
        self.target = target


_P = ParamSpec("_P")
_T = TypeVar("_T")

_P1 = ParamSpec("_P1")
_T1 = TypeVar("_T1")

_TboundTrait = TypeVar("_TboundTrait", bound=Trait)


class Fn(Generic[_P, _T]):
    __attr__: str
    schema: Callable[_P, Awaitable[_T]]

    @overload
    def __new__(cls, schema: Callable[Concatenate[_TboundTrait, _P1], Awaitable[_T1]]) -> Fn[_P1, _T1]:
        ...

    @overload
    def __new__(cls, schema: Callable[_P1, Awaitable[_T1]]) -> Fn[_P1, _T1]:
        ...

    def __new__(cls, schema: ...) -> ...:
        instance = super().__new__(cls)
        instance.schema = schema
        return instance

    def __set_name__(self, owner: type[Trait], attr: str):
        self.__attr__ = attr

    @overload
    def __get__(self, instance: Trait, owner: type[Trait]) -> FnWrapper[_P, _T]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type[Trait] | None) -> Self:
        ...

    def __get__(self, instance: ..., owner: ...) -> Self | FnWrapper[_P, _T]:
        # sourcery skip: assign-if-exp, reintroduce-else, swap-if-expression
        if not isinstance(instance, Trait):
            return self
        return FnWrapper(instance, self)


class FnWrapper(Generic[_P, _T]):
    _args: tuple[Any, ...] | None = None
    _kwargs: dict[str, Any] | None = None
    trait: Trait

    def __init__(self, trait: Trait, fn: Fn[_P, _T]):
        self.trait = trait
        self.fn = fn

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs):
        self._args = args
        self._kwargs = kwargs
        return self

    def __await__(self):
        return self.__await_impl__().__await__()

    async def __await_impl__(self) -> _T:
        if self._args is None or self._kwargs is None:
            raise ValueError("cannot call without param in shape of schema")

        impl = self.trait.relationship._artifacts.get(
            Impl(
                self.fn,
                None,
                self.trait.path,
            )
        )
        if impl is None:
            raise NotImplementedError(
                f'"{identity(self.trait)}::{self.fn.__attr__}" '
                f'in "{identity(self.trait.relationship.protocol)}" '
                + (f'for target "{self.trait.target.path_without_land}"' if self.trait.target is not None else "")
                + "is not implemented"
            )
        impl = cast("Callable[Concatenate[Context, _P], Awaitable[_T]]", impl)
        return await impl(self.trait.relationship, *self._args, **self._kwargs)  # type: ignore


class OrientedFn(Fn[_P, _T]):
    # 要求 Trait 里面要设置对象

    @overload
    def __new__(cls, schema: Callable[Concatenate[_TboundTrait, _P1], Awaitable[_T1]]) -> OrientedFn[_P1, _T1]:
        ...

    @overload
    def __new__(cls, schema: Callable[_P1, Awaitable[_T1]]) -> OrientedFn[_P1, _T1]:
        ...

    def __new__(cls, schema: ...) -> ...:
        return super().__new__(cls, schema)

    @overload
    def __get__(self, instance: Trait, owner: type[Trait]) -> OrientedFnWrapper[_P, _T]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type[Trait] | None) -> Self:
        ...

    def __get__(self, instance: ..., owner: ...) -> ...:
        # sourcery skip: assign-if-exp, reintroduce-else
        if instance is None:
            return self
        return DirectFnWrapper(instance, self)


class OrientedFnWrapper(FnWrapper[_P, _T]):
    _args: tuple[Any, ...] | None = None
    _kwargs: dict[str, Any] | None = None

    async def __await_impl__(self) -> _T:
        if self._args is None or self._kwargs is None:
            raise ValueError("cannot call without param in shape of schema")

        target = self.trait.target
        if target is None:
            raise ValueError(f'cannot call "{identity(self.trait)}::{self.fn.__attr__}" without target on cast')
        impl = self.trait.relationship._artifacts.get(
            Impl(
                self.fn,
                target.path_without_land,
                self.trait.path,
            )
        )
        if impl is None:
            debug(
                self.trait.relationship._artifacts,
                Impl(
                    self.fn,
                    target.path_without_land,
                    self.trait.path,
                ),
            )
            raise NotImplementedError(
                f'"{identity(self.trait)}::{self.fn.__attr__}" '
                f'in "{identity(self.trait.relationship.protocol)}" '
                f'for target "{target.path_without_land}" '
                "is not implemented"
            )
        impl = cast("Callable[Concatenate[Context, Selector, _P], Awaitable[_T]]", impl)
        return await impl(self.trait.relationship, target, *self._args, **self._kwargs)  # type: ignore


class DirectFn(Fn[_P, _T]):
    @overload
    def __new__(cls, schema: Callable[Concatenate[_TboundTrait, _P1], Awaitable[_T1]]) -> DirectFn[_P1, _T1]:
        ...

    @overload
    def __new__(cls, schema: Callable[_P1, Awaitable[_T1]]) -> DirectFn[_P1, _T1]:
        ...

    def __new__(cls, schema: ...) -> ...:
        return super().__new__(cls, schema)

    @overload
    def __get__(self, instance: Trait, owner: type[Trait]) -> DirectFnWrapper[_P, _T]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type[Trait] | None) -> Self:
        ...

    def __get__(self, instance: ..., owner: ...) -> ...:
        # sourcery skip: assign-if-exp, reintroduce-else
        if instance is None:
            return self
        return DirectFnWrapper(instance, self)


class DirectFnWrapper(FnWrapper[_P, _T]):
    target: Selector | None = None

    def to(self, target: Selector):
        self.target = target
        return self

    async def __await_impl__(self) -> _T:
        if self._args is None or self._kwargs is None:
            raise ValueError("cannot call without param in shape of schema")

        target = self.target or self.trait.target
        if target is None:
            targetter = self.trait.relationship._artifacts.get(ImplDefaultTarget(self.trait.path, self.fn))
            if targetter is None:
                raise NotImplementedError(
                    f'"{self.trait.__class__.__name__}::{self.fn.__attr__}" '
                    "required a target, but no target given and no default getter implemented."
                )
            targetter = cast("Callable[[Context], Selector]", targetter)
            target = targetter(self.trait.relationship)
        impl = self.trait.relationship._artifacts.get(
            Impl(
                self.fn,
                target.path_without_land,
                self.trait.path,
            )
        )
        if impl is None:
            debug(
                self.trait.relationship._artifacts,
                Impl(
                    self.fn,
                    target.path_without_land,
                    self.trait.path,
                ),
            )
            raise NotImplementedError(
                f'"{self.trait.__class__.__name__}::{self.fn.__attr__}" '
                f'in "{self.trait.relationship.protocol.__class__.__name__}" '
                f'for target "{target.path_without_land}" '
                "is not implemented"
            )
        impl = cast("Callable[Concatenate[Context, Selector, _P], Awaitable[_T]]", impl)
        return await impl(self.trait.relationship, target, *self._args, **self._kwargs)  # type: ignore
