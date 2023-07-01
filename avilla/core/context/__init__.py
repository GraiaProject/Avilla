from __future__ import annotations

from collections.abc import Callable
from functools import partial, reduce
from typing import TYPE_CHECKING, Any, TypedDict, TypeVar, cast, overload

from typing_extensions import ParamSpec, Self, Unpack

from avilla.core._runtime import cx_context
from avilla.core.account import BaseAccount
from avilla.core.metadata import Metadata, MetadataRoute
from avilla.core.platform import Land
from avilla.core.resource import Resource
from avilla.core.ryanvk.capability import CoreCapability
from avilla.core.ryanvk.collector.context import ContextCollector
from avilla.core.ryanvk.common.protocol import Executable
from avilla.core.ryanvk.common.runner import Runner as BaseRunner
from avilla.core.selector import (
    FollowsPredicater,
    Selectable,
    Selector,
    _FollowItem,
    _parse_follows,
)
from avilla.core.utilles import classproperty

from ._query import QueryHandler, find_querier_steps, query_depth_generator
from ._selector import (
    ContextClientSelector,
    ContextEndpointSelector,
    ContextMedium,
    ContextRequestSelector,
    ContextSceneSelector,
    ContextSelector,
)

if TYPE_CHECKING:
    from avilla.core.ryanvk.descriptor.query import QueryHandlerPerform

P = ParamSpec("P")
R = TypeVar("R", covariant=True)
_T = TypeVar("_T")
_MetadataT = TypeVar("_MetadataT", bound=Metadata)


class ContextCache(TypedDict):
    meta: dict[Selector, dict[type[Metadata] | MetadataRoute, Metadata]]


class Context(BaseRunner):
    account: BaseAccount

    client: ContextClientSelector
    endpoint: ContextEndpointSelector
    scene: ContextSceneSelector
    self: Selector
    mediums: list[ContextMedium]

    cache: ContextCache | dict[str, Any]

    def __init__(
        self,
        account: BaseAccount,
        client: Selector,
        endpoint: Selector,
        scene: Selector,
        selft: Selector,
        mediums: list[Selector] | None = None,
        prelude_metadatas: dict[Selector, dict[type[Metadata] | MetadataRoute, Metadata]] | None = None,
    ) -> None:
        super().__init__()
        self.artifacts.maps = [
            account.info.isolate.artifacts,
            account.info.protocol.isolate.artifacts,
            account.avilla.isolate.artifacts,
        ]

        self.account = account

        self.client = ContextClientSelector.from_selector(self, client)
        self.endpoint = ContextEndpointSelector.from_selector(self, endpoint)
        self.scene = ContextSceneSelector.from_selector(self, scene)
        self.self = selft
        self.mediums = [ContextMedium(ContextSelector.from_selector(self, medium)) for medium in mediums or []]

        self.cache = {"meta": prelude_metadatas or {}}

    @property
    def protocol(self):
        return self.account.info.protocol

    @property
    def avilla(self):
        return self.protocol.avilla

    @property
    def land(self):
        return self.account.info.platform[Land]

    @property
    def request(self) -> ContextRequestSelector:
        return self.endpoint.expects_request()

    @property
    def is_resource(self) -> bool:
        return any(isinstance(i, Resource) for i in self.cache["meta"].get(self.endpoint, {}).values())

    def _collect_metadatas(self, target: Selector | Selectable, *metadatas: Metadata):
        scope = self.cache["meta"].setdefault(target.to_selector(), {})
        scope.update({type(i): i for i in metadatas})

    @classproperty
    @classmethod
    def current(cls) -> Context:
        return cx_context.get()

    async def query(self, pattern: str, **predicators: FollowsPredicater):
        items = _parse_follows(pattern, **predicators)
        steps = find_querier_steps(self.artifacts, items)
        if steps is None:
            return

        def build_handler(artifact: Executable[Self, [], Any]) -> QueryHandler:
            collector, entity = cast(
                "tuple[ContextCollector, QueryHandlerPerform]",
                artifact,
            )
            instance = collector.cls(self)
            return partial(entity, instance)

        def build_predicate(_steps: tuple[_FollowItem, ...]) -> Callable[[str, str], bool]:
            mapping = {i.name: i for i in _steps}

            def predicater(key: str, value: str) -> bool:
                if key not in mapping:
                    raise KeyError(f"expected existed key: {key}")
                item = mapping[key]
                if item.literal is not None:
                    return value == item.literal
                elif item.predicate is not None:
                    return item.predicate(value)
                return True

            return predicater

        handlers = map(lambda x: (x[0], build_handler(self.artifacts[x[1]])), steps)
        r = reduce(
            lambda previous, current: query_depth_generator(current[1], build_predicate(current[0]), previous),
            handlers,
            None,
        )
        if TYPE_CHECKING:
            assert r is not None
        async for i in r:
            yield i

    async def fetch(self, resource: Resource[_T]) -> _T:
        #return await self[](resource)
        ... # TODO

    async def pull(
        self,
        route: type[_MetadataT] | MetadataRoute[Unpack[tuple[Any, ...]], _MetadataT],
        target: Selector | Selectable,
        *,
        flush: bool = False,
    ) -> _MetadataT:
        if isinstance(target, Selectable):
            target = target.to_selector()

        cached = self.cache["meta"].get(target)
        if cached is not None and route in cached:
            if flush:
                del cached[route]
            elif not route.has_params():
                return cast("_MetadataT", cached[route])

        return await self[CoreCapability.pull.into(route)](target, route)

    @overload
    def __getitem__(self, closure: Selector) -> ContextSelector:
        ...

    @overload
    def __getitem__(self, closure: Executable[Context, P, R]) -> Callable[P, R]:
        ...

    def __getitem__(self, closure: Selector | Executable[Context, P, Any]) -> Any:
        if isinstance(closure, Selector):
            return ContextSelector(self, closure.pattern)
        return partial(self.execute, closure)
