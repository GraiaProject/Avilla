from __future__ import annotations

from collections.abc import Awaitable, Callable, Container, Iterable
from functools import partial
from inspect import isawaitable
from operator import contains, eq, is_, is_not, ne
from typing import Any, Generic, TypeVar

from graia.broadcast import BaseDispatcher, DispatcherInterface, ExecutionStop
from typing_extensions import ParamSpec, Self

from avilla.core.account import AbstractAccount
from avilla.core.context import Context
from avilla.core.selector import Selectable, Selector
from avilla.core.utilles import classproperty

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

    def match(self: Filter[Selectable], pattern: Selector) -> Filter[Selectable]:
        return self.assert_true(lambda result: pattern.matches(result))

    def mismatch(self: Filter[Selectable], pattern: Selector) -> Filter[Selectable]:
        return self.assert_false(lambda result: pattern.matches(result))

    def match_any(self: Filter[Selectable], patterns: Iterable[Selector]) -> Filter[Selectable]:
        return self.any(lambda result: pattern.matches(result) for pattern in patterns)

    def match_all(self: Filter[Selectable], patterns: Iterable[Selector]) -> Filter[Selectable]:
        return self.all(lambda result: pattern.matches(result) for pattern in patterns)

    def mismatch_any(self: Filter[Selectable], patterns: Iterable[Selector]) -> Filter[Selectable]:
        return self.any(lambda result: not pattern.matches(result) for pattern in patterns)

    def mismatch_all(self: Filter[Selectable], patterns: Iterable[Selector]) -> Filter[Selectable]:
        return self.any(lambda result: not pattern.matches(result) for pattern in patterns)

    def follows(self: Filter[Selectable], *patterns: str) -> Filter[Selectable]:
        return self.any(lambda result: result.to_selector().follows(pattern) for pattern in patterns)

    @classproperty
    @classmethod
    def ctx(cls) -> Filter[Context]:
        return cls().fetch(Context)

    @property
    def client(self: Filter[Context]) -> Filter[Selectable]:
        return self.ctx.step(lambda ctx: ctx.client)

    @property
    def scene(self: Filter[Context]) -> Filter[Selector]:
        return self.ctx.step(lambda ctx: ctx.scene)

    @property
    def account(self: Filter[Context]) -> Filter[AbstractAccount]:
        return self.ctx.step(lambda ctx: ctx.account)

    @property
    def mediums_first(self: Filter[Context]) -> Filter[Selector | None]:
        return self.ctx.step(lambda ctx: ctx.mediums[0].selector if ctx.mediums else None)

    async def beforeExecution(self, interface: DispatcherInterface):
        result: Awaitable[Any] | Any = interface  # type: ignore
        for middleware in self.middlewares:
            if isawaitable(result := middleware(result)):
                result = await result

    async def catch(self, interface: DispatcherInterface):
        return interface.local_storage.get("__filter_fetch__", {}).get(interface.annotation)
