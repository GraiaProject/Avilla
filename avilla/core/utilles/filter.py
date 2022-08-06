from __future__ import annotations

from collections.abc import Callable, Container, Iterable
from functools import partial
from inspect import isawaitable
from operator import contains, eq, is_, is_not, ne
from typing import Any, Awaitable, Generic, ParamSpec, TypeVar

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

    def assert_true(self, func: Callable[[T], Any]) -> Self:
        @self.step
        def _(result: T) -> T:
            if func(result):
                return result
            raise ExecutionStop

        return self

    def assert_false(self, func: Callable[[T], Any]) -> Self:
        return self.assert_true(lambda result: not func(result))

    def assert_equal(self, value: R) -> R:
        return self.assert_true(partial(eq, value))  # type: ignore

    def assert_not_equal(self, value: Any) -> Self:
        return self.assert_true(partial(ne, value))

    def assert_is(self, value: R) -> Filter[R]:
        return self.assert_true(partial(is_, value))  # type: ignore

    def assert_is_not(self, value: Any) -> Self:
        return self.assert_true(partial(is_not, value))

    def assert_is_none(self) -> Filter[None]:
        return self.assert_is(None)

    def assert_is_not_none(self) -> Self:  # 实际上类型是 Filter[T - None]
        return self.assert_is_not(None)

    def assert_in(self, container: Container[R]) -> Filter[R]:
        return self.assert_true(partial(contains, container))  # type: ignore

    def assert_not_in(self, container: Container) -> Self:
        return self.assert_true(lambda result: result not in container)

    def assert_is_instance(self, cls: type[R]) -> Filter[R]:
        return self.assert_true(lambda result: isinstance(result, cls))  # type: ignore

    def assert_not_is_instance(self, cls: type) -> Self:
        return self.assert_true(lambda result: not isinstance(result, cls))

    def any(self, funcs: Iterable[Callable[[T], Any]]) -> Self:
        funcs = frozenset(funcs)
        return self.assert_true(lambda result: any(func(result) for func in funcs))

    def all(self, funcs: Iterable[Callable[[T], Any]]) -> Self:
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
    @property
    def rs(cls) -> Filter[Relationship]:
        return cls().fetch(Relationship)

    @property
    def ctx(self: Filter[Relationship]) -> Filter[Selector]:
        return self.rs.step(lambda rs: rs.ctx)

    @property
    def mainline(self: Filter[Relationship]) -> Filter[Selector]:
        return self.rs.step(lambda rs: rs.mainline)

    @property
    def current(self: Filter[Relationship]) -> Filter[AbstractAccount]:
        return self.rs.step(lambda rs: rs.current)

    @property
    def via(self: Filter[Relationship]) -> Filter[Selector | None]:
        return self.rs.step(lambda rs: rs.via)

    async def beforeExecution(self, interface: DispatcherInterface):
        result: Awaitable[Any] | Any = interface  # type: ignore
        for middleware in self.middlewares:
            if isawaitable(result := middleware(result)):
                result = await result

    async def catch(self, interface: DispatcherInterface):
        return interface.local_storage.get("__filter_fetch__", {}).get(interface.annotation)
