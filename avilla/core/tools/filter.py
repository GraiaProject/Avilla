from __future__ import annotations

from collections.abc import Awaitable, Callable, Container, Iterable
from functools import partial
from inspect import isawaitable
from operator import contains, eq, is_, is_not, ne
from typing import Any, Generic, Protocol, TypeVar

from typing_extensions import ParamSpec, Self

from avilla.core.account import BaseAccount
from avilla.core.context import Context
from avilla.core.event import MetadataModified
from avilla.core.selector import Selectable, Selector
from avilla.core.utilles import classproperty
from graia.broadcast import BaseDispatcher, DispatcherInterface, ExecutionStop

T = TypeVar("T", covariant=True)
R = TypeVar("R")
P = ParamSpec("P")


class _ClientSpecified(Protocol[R]):
    client: R


class _EndpointSpecified(Protocol[R]):
    endpoint: R


class _SceneSpecified(Protocol[R]):
    scene: R


class _SelfSpecified(Protocol[R]):
    self: R


class Filter(BaseDispatcher, Generic[T]):
    middlewares: list[Callable[[Any], Awaitable[Any] | Any]]

    def __init__(self):
        self.middlewares = []

    def dispatch(self, annotation: type[R]) -> Filter[R]:
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

    def assert_true(self: Filter[R], func: Callable[[R], Any]):
        @self.step
        def _(result: R) -> R:
            if func(result):
                return result
            raise ExecutionStop

        return self

    def assert_false(self, func: Callable[[T], Any]) -> Self:
        return self.assert_true(lambda result: not func(result))

    def assert_equal(self, value: Any) -> Self:
        return self.assert_true(partial(eq, value))

    def assert_not_equal(self, value: Any) -> Self:
        return self.assert_true(partial(ne, value))

    def is_(self, value: Any):
        return self.assert_true(partial(is_, value))

    def is_not(self, value: Any) -> Self:
        return self.assert_true(partial(is_not, value))

    def is_none(self):
        return self.is_(None)

    def is_not_none(self) -> Self:  # 实际上类型是 Filter[T - None]
        return self.is_not(None)

    def contains(self, container: Container[R]) -> Filter[R]:
        return self.assert_true(partial(contains, container))  # type: ignore

    def not_contains(self, container: Container) -> Self:
        return self.assert_true(lambda result: result not in container)

    def instanceof(self, cls: type[R]) -> Filter[R]:
        return self.assert_true(lambda result: isinstance(result, cls))  # type: ignore

    def not_instanceof(self, cls: type) -> Self:
        return self.assert_true(lambda result: not isinstance(result, cls))

    def any(self, funcs: Iterable[Callable[[T], Any]]) -> Self:
        funcs = frozenset(funcs)
        return self.assert_true(lambda result: any(func(result) for func in funcs))

    def all(self, funcs: Iterable[Callable[[T], Any]]) -> Self:
        funcs = frozenset(funcs)
        return self.assert_true(lambda result: all(func(result) for func in funcs))

    def follows(self: Filter[Selectable], *patterns: str) -> Filter[Selectable]:
        return self.any(lambda result: result.to_selector().follows(pattern) for pattern in patterns)

    @classproperty
    @classmethod
    def cx(cls) -> Filter[Context]:
        return cls().dispatch(Context)

    @property
    def client(self: Filter[_ClientSpecified[R]]) -> Filter[R]:
        return self.step(lambda x: x.client)

    @property
    def scene(self: Filter[_SceneSpecified[R]]) -> Filter[R]:
        return self.step(lambda x: x.scene)

    @property
    def endpoint(self: Filter[_EndpointSpecified[R]]) -> Filter[R]:
        return self.step(lambda x: x.endpoint)

    @property
    def self(self: Filter[_SelfSpecified[R]]) -> Filter[R]:
        return self.step(lambda x: x.self)

    @classmethod
    def account(cls) -> Filter[BaseAccount]:
        return cls.cx.step(lambda cx: cx.account)

    def medium(self: Filter[Context], index: int = 0) -> Filter[Selector | None]:
        return self.cx.step(lambda cx: cx.mediums[index].selector if cx.mediums else None)

    @classproperty
    @classmethod
    def mod(cls) -> Filter[MetadataModified]:
        return cls().dispatch(MetadataModified)

    async def beforeExecution(self, interface: DispatcherInterface):
        result: Awaitable[Any] | Any = interface  # type: ignore
        for middleware in self.middlewares:
            if isawaitable(result := middleware(result)):
                result = await result

    async def catch(self, interface: DispatcherInterface):
        return interface.local_storage.get("__filter_fetch__", {}).get(interface.annotation)


if __name__ == "__main__":
    print(Filter().scene.follows("group").middlewares)
