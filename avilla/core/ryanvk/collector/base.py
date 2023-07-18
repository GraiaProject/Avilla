from __future__ import annotations

from contextlib import AbstractContextManager, asynccontextmanager
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    ClassVar,
    Protocol,
    TypeVar,
    overload,
)

from typing_extensions import ParamSpec, Self, Unpack

from avilla.core.ryanvk._runtime import processing_isolate
from avilla.core.ryanvk.collector.access import Access
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


class PerformTemplate:
    __collector__: ClassVar[BaseCollector]
    components: dict[str, Any]

    def __init__(self, components: dict[str, Any]):
        self.components = components

    @classmethod
    def entrypoints(cls):
        return [k for k, v in cls.__dict__.items() if isinstance(v, Access)]

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
    post_applying: bool = False

    def __init__(self):
        self.artifacts = {"current_collection": {}}
        self.defer_callbacks = [self.__post_collected__]

    @property
    def cls(self: _ResultCollect[R]) -> R:
        if TYPE_CHECKING:
            return self._
        return self._cls

    @property
    def _(self):
        return self.get_collect_template()

    def __post_collected__(self, cls: type[PerformTemplate]):
        self._cls = cls
        if self.post_applying:
            if (isolate := processing_isolate.get(None)) is not None:
                isolate.apply(cls)

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

    def with_(self, context_manager: AbstractContextManager[T]) -> T:
        self.defer(lambda _: context_manager.__exit__(None, None, None))
        return context_manager.__enter__()

    def apply_defering(self, isolate: Isolate):
        self.defer(lambda x: isolate.apply(x))

    def entity(self, signature: SupportsCollect[Self, P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        return signature.collect(self, *args, **kwargs)

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
