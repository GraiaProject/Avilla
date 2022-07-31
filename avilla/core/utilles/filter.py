from __future__ import annotations

from collections.abc import Callable, Container, Iterable
from functools import partial
from inspect import _empty, isawaitable
from operator import contains, eq, is_, is_not, ne, not_
from typing import Any, Awaitable, Generic, ParamSpec, TypeVar, overload

from graia.broadcast import BaseDispatcher, DispatcherInterface, ExecutionStop
from typing_extensions import Self

from avilla.core.account import AbstractAccount
from avilla.core.relationship import Relationship
from avilla.core.utilles.selector import Selector

T = TypeVar("T")
R = TypeVar("R")
P = ParamSpec("P")


class Filter(BaseDispatcher, Generic[T]):
    middlewares: list[Callable[[Any], Awaitable[Any] | Any]]

    def fetch(self, annotation: type[R]) -> Filter[R]:
        @self.middlewares.append
        async def _(_) -> R:
            interface = DispatcherInterface.ctx.get()
            result = await interface.lookup_param("__filter_fetch__", annotation, None)
            interface.local_storage.setdefault("__filter_fetch__", {})[annotation] = result
            return result

        return self  # type: ignore

    def step(self, func: Callable[[T], R]) -> Filter[R]:
        self.middlewares.append(func)
        return self  # type: ignore

    def assert_true(self, func: Callable[[T], Any] | None = None) -> Self:
        if func is None:

            def inner(result: T) -> T:
                if result:
                    return result
                raise ExecutionStop

        else:

            def inner(result: T) -> T:
                if func(result):
                    return result
                raise ExecutionStop

        return self.step(inner)

    def assert_false(self, func: Callable[[T], bool] | None = None) -> Self:
        return self.assert_true(not_) if func is None else self.assert_true(lambda result: not func(result))

    @overload
    def assert_equal(self, value: Any, /) -> Self:
        ...

    @overload
    def assert_equal(self, func: Callable[[T], Any], value: Any, /) -> Self:
        ...

    def assert_equal(self, func_or_value: Callable[[T], Any] | Any, value: Any = _empty, /) -> Self:
        return (
            self.assert_true(partial(eq, func_or_value))
            if value is _empty
            else self.assert_true(lambda result: func_or_value(result) == value)
        )

    @overload
    def assert_not_equal(self, value: Any, /) -> Self:
        ...

    @overload
    def assert_not_equal(self, func: Callable[[T], Any], value: Any, /) -> Self:
        ...

    def assert_not_equal(self, func_or_value: Callable[[T], Any] | Any, value: Any = _empty, /) -> Self:
        return (
            self.assert_true(partial(ne, func_or_value))
            if value is _empty
            else self.assert_true(lambda result: func_or_value(result) != value)
        )

    @overload
    def assert_is(self, value: Any, /) -> Self:
        ...

    @overload
    def assert_is(self, func: Callable[[T], Any], value: Any, /) -> Self:
        ...

    def assert_is(self, func_or_value: Callable[[T], Any] | Any, value: Any = _empty, /) -> Self:
        return (
            self.assert_true(partial(is_, func_or_value))
            if value is _empty
            else self.assert_true(lambda result: func_or_value(result) is value)
        )

    @overload
    def assert_is_not(self, value: Any, /) -> Self:
        ...

    @overload
    def assert_is_not(self, func: Callable[[T], Any], value: Any, /) -> Self:
        ...

    def assert_is_not(self, func_or_value: Callable[[T], Any] | Any, value: Any = _empty, /) -> Self:
        return (
            self.assert_true(partial(is_not, func_or_value))
            if value is _empty
            else self.assert_true(lambda result: func_or_value(result) is not value)
        )

    def assert_is_none(self, func: Callable[[T], Any] | None = None) -> Self:
        return self.assert_is(None) if func is None else self.assert_is(func, None)

    def assert_is_not_none(self, func: Callable[[T], Any] | None = None) -> Self:
        return self.assert_is_not(None) if func is None else self.assert_is_not(func, None)

    @overload
    def assert_in(self, container: Container, /) -> Self:
        ...

    @overload
    def assert_in(self, func: Callable[[T], Any], container: Container, /) -> Self:
        ...

    def assert_in(
        self,
        func_or_container: Callable[[T], Any] | Container,
        container: Container | None = None,
        /,
    ) -> Self:
        return (
            self.assert_true(partial(contains, func_or_container))  # type: ignore
            if container is None
            else self.assert_true(lambda result: func_or_container(result) in container)  # type: ignore
        )

    @overload
    def assert_not_in(self, container: Container, /) -> Self:
        ...

    @overload
    def assert_not_in(self, func: Callable[[T], Any], container: Container, /) -> Self:
        ...

    def assert_not_in(
        self,
        func_or_container: Callable[[T], Any] | Container,
        container: Container | None = None,
        /,
    ) -> Self:
        return (
            self.assert_true(lambda result: result not in func_or_container)  # type: ignore
            if container is None
            else self.assert_true(lambda result: func_or_container(result) not in container)  # type: ignore
        )

    @overload
    def assert_is_instance(self, cls: type[Any], /) -> Self:
        ...

    @overload
    def assert_is_instance(self, func: Callable[[T], Any], cls: type[Any], /) -> Self:
        ...

    def assert_is_instance(
        self, func_or_cls: Callable[[T], Any] | type[Any], cls: type[Any] | None = None, /
    ) -> Self:
        return (
            self.assert_true(lambda result: isinstance(result, func_or_cls))  # type: ignore
            if cls is None
            else self.assert_true(lambda result: isinstance(func_or_cls(result), cls))
        )

    @overload
    def assert_not_is_instance(self, cls: type[Any], /) -> Self:
        ...

    @overload
    def assert_not_is_instance(self, func: Callable[[T], Any], cls: type[Any], /) -> Self:
        ...

    def assert_not_is_instance(
        self, func_or_cls: Callable[[T], Any] | type[Any], cls: type[Any] | None = None, /
    ) -> Self:
        return (
            self.assert_true(lambda result: not isinstance(result, func_or_cls))  # type: ignore
            if cls is None
            else self.assert_true(lambda result: not isinstance(func_or_cls(result), cls))
        )

    def any(self, funcs: Iterable[Callable[[T], bool]]) -> Self:
        funcs = frozenset(funcs)
        return self.assert_true(lambda result: any(func(result) for func in funcs))

    def all(self, funcs: Iterable[Callable[[T], bool]]) -> Self:
        funcs = frozenset(funcs)
        return self.assert_true(lambda result: all(func(result) for func in funcs))

    def match(self: Filter[Selector], pattern: Selector) -> Filter[Selector]:
        return self.assert_true(lambda result: result.match(pattern))

    def mismatch(self: Filter[Selector], pattern: Selector) -> Filter[Selector]:
        return self.assert_false(lambda result: result.match(pattern))

    def match_any(self: Filter[Selector], patterns: Iterable[Selector]) -> Filter[Selector]:
        return self.any(lambda result: result.match(pattern) for pattern in patterns)

    def match_all(self: Filter[Selector], patterns: Iterable[Selector]) -> Filter[Selector]:
        return self.all(lambda result: result.match(pattern) for pattern in patterns)

    def mismatch_any(self: Filter[Selector], patterns: Iterable[Selector]) -> Filter[Selector]:
        return self.any(lambda result: not result.match(pattern) for pattern in patterns)

    def mismatch_all(self: Filter[Selector], patterns: Iterable[Selector]) -> Filter[Selector]:
        return self.all(lambda result: not result.match(pattern) for pattern in patterns)

    @classmethod
    def rs(cls) -> Filter[Relationship]:
        return cls().fetch(Relationship)

    @classmethod
    def ctx(cls) -> Filter[Selector]:
        return cls.rs().step(lambda rs: rs.ctx)

    @classmethod
    def mainline(cls) -> Filter[Selector]:
        return cls.rs().step(lambda rs: rs.mainline)

    @classmethod
    def current(cls) -> Filter[AbstractAccount]:
        return cls.rs().step(lambda rs: rs.current)

    @classmethod
    def via(cls) -> Filter[Selector | None]:
        return cls.rs().step(lambda rs: rs.via)

    async def beforeExecution(self, interface: DispatcherInterface):
        result: Awaitable[Any] | Any = interface  # type: ignore
        for middleware in self.middlewares:
            if isawaitable(result := middleware(result)):
                result = await result

    async def catch(self, interface: DispatcherInterface):
        return interface.local_storage.setdefault("__filter_fetch__", {}).get(interface.annotation)
