from __future__ import annotations

from contextlib import AbstractContextManager, AsyncExitStack, asynccontextmanager
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    ClassVar,
    Iterable,
    Protocol,
    TypeVar,
    overload,
)

from typing_extensions import ParamSpec, Self, Unpack

from avilla.core.ryanvk._runtime import ARTIFACT_COLLECTIONS, processing_isolate
from avilla.core.ryanvk.descriptor.base import OverridePerformEntity
from avilla.core.ryanvk.descriptor.fetch import Fetch
from avilla.core.ryanvk.endpoint import Endpoint
from avilla.core.ryanvk.isolate import _merge_lookup_collection
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
    targets: ClassVar[Iterable[str]] = ()
    components: dict[str, Any]
    dispatched_overrides: dict[tuple[type[PerformTemplate], str], Any]

    def __init__(self, components: dict[str, Any], dispatched_overrides: dict[tuple[type[PerformTemplate], str], Any]):
        self.components = components
        self.dispatched_overrides = dispatched_overrides

    @classmethod
    def endpoints(cls):
        return [(k, v) for k, v in cls.__dict__.items() if isinstance(v, Endpoint)]

    @classmethod
    def overrides(cls):
        return [(k, v) for k, v in cls.__dict__.items() if isinstance(v, OverridePerformEntity)]

    @asynccontextmanager
    async def run_with_lifespan(self):
        async with AsyncExitStack() as stack:
            for _, v in self.endpoints():
                await stack.enter_async_context(v.lifespan(self))
            yield self

    @classmethod
    def __post_collected__(cls, collect: BaseCollector):
        ...

    def __init_subclass__(cls, *, native: bool = False) -> None:
        if native:
            return

        collector = cls.__collector__
        artifacts = collector.artifacts

        for i in collector.defer_callbacks:
            i(cls)

        cls.__post_collected__(collector)

        current_collection = None
        if "current_collection" in artifacts:
            current_collection = artifacts["current_collection"]

        for target in cls.targets:
            lookup_collection = {}
            target_artifacts = ARTIFACT_COLLECTIONS.setdefault(target, {"lookup_collections": [lookup_collection]})
            if current_collection is not None:
                _merge_lookup_collection(lookup_collection, current_collection)
            target_artifacts.update({k: v for k, v in artifacts if k != "current_collection"})


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
        class LocalPerformTemplate(PerformTemplate, native=True):
            __collector__ = self

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
