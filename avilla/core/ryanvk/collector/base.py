from __future__ import annotations

from contextlib import AbstractContextManager, asynccontextmanager
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Protocol,
    TypeVar,
    overload,
)

from typing_extensions import ParamSpec, Self, Unpack

from avilla.core.ryanvk.descriptor.fetch import Fetch
from avilla.core.ryanvk.protocol import SupportsCollect
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from avilla.core.metadata import Metadata, MetadataRoute
    from avilla.core.ryanvk.isolate import Isolate
    from avilla.core.selector import FollowsPredicater


P = ParamSpec("P")
R = TypeVar("R", covariant=True)
T = TypeVar("T")
M = TypeVar("M", bound="Metadata")


class ComponentEntrypoint(Generic[T]):
    name: str

    def __init__(self):
        ...

    def __set_name__(self, owner: type, name: str):
        self.name = name

    @overload
    def __get__(self, instance: None, owner: type) -> Self:
        ...

    @overload
    def __get__(self, instance: PerformTemplate, owner: type) -> T:
        ...

    def __get__(self, instance: PerformTemplate | None, owner: type):
        if instance is None:
            return self

        return instance.components[self.name]


class PerformTemplate:
    __collector__: ClassVar[BaseCollector]
    components: dict[str, Any]

    def __init__(self, components: dict[str, Any]):
        self.components = components

    @classmethod
    def entrypoints(cls):
        return [k for k, v in cls.__dict__.items() if isinstance(v, ComponentEntrypoint)]

    @asynccontextmanager
    async def run_with_lifespan(self):
        # TODO
        yield self
    
    @classmethod
    def __post_collected__(cls, collect: BaseCollector):
        ...


class _ResultCollect(Protocol[R]):
    @property
    def _(self) -> R:
        ...


class BaseCollector:
    artifacts: dict[Any, Any]
    defer_callbacks: list[Callable[[type[PerformTemplate]], Any]]

    def __init__(self):
        self.artifacts = {"current_collection": {}}
        self.defer_callbacks = [self.__post_collect__]

    @property
    def cls(self: _ResultCollect[R]) -> R:
        if TYPE_CHECKING:
            return self._
        return self._cls

    @property
    def _(self):
        return self.get_collect_template()


    def entity(self, signature: SupportsCollect[Self, P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        return signature.collect(self, *args, **kwargs)

    def get_collect_template(self):
        class LocalPerformTemplate(PerformTemplate):
            __collector__ = self

            def __init_subclass__(cls) -> None:
                if getattr(cls, "__native__", False):
                    delattr(cls, "__native__")
                    return

                for i in self.defer_callbacks:
                    i(cls)
                
                cls.__post_collected__(self)

        return LocalPerformTemplate

    def defer(self, func: Callable[[type], Any]):
        self.defer_callbacks.append(func)

    def x(self, context_manager: AbstractContextManager[T]) -> T:
        self.defer(lambda _: context_manager.__exit__(None, None, None))
        return context_manager.__enter__()

    def apply(self, isolate: Isolate):
        self.defer(lambda x: isolate.apply(x))

    @overload
    def pull(
        self, target: str, route: type[M], **patterns: FollowsPredicater
    ) -> Callable[[Callable[[Any, Selector], Awaitable[M]]], Callable[[Any, Selector], Awaitable[M]]]:
        ...

    @overload
    def pull(
        self, target: str, route: MetadataRoute[Unpack[tuple[Any, ...]], M], **patterns: FollowsPredicater
    ) -> Callable[[Callable[[Any, Selector], Awaitable[M]]], Callable[[Any, Selector], Awaitable[M]]]:
        ...

    def pull(self, target: str, route: ..., **patterns: FollowsPredicater) -> ...:
        from avilla.core.builtins.capability import CoreCapability

        return self.entity(CoreCapability.pull, target, route, **patterns)

    def fetch(self, resource_type: type[T]):  # type: ignore[reportInvalidTypeVarUse]
        return self.entity(Fetch, resource_type)

    def __post_collect__(self, cls: type[PerformTemplate]):
        self._cls = cls
