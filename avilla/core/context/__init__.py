from __future__ import annotations

from collections import ChainMap
from collections.abc import Callable
from functools import reduce
from typing import TYPE_CHECKING, Any, Awaitable, TypedDict, TypeVar, cast, overload

from typing_extensions import ParamSpec, Unpack

from avilla.core._runtime import cx_context
from avilla.core.account import BaseAccount
from avilla.core.builtins.capability import CoreCapability
from avilla.core.metadata import Metadata, MetadataRoute
from avilla.core.platform import Land
from avilla.core.resource import Resource
from avilla.core.ryanvk.collector.base import BaseCollector
from avilla.core.ryanvk.descriptor.base import Fn
from avilla.core.ryanvk.runner import run_fn, use_record
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


class Context:
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
        self.artifacts = ChainMap(
            account.info.isolate.artifacts,
            account.info.protocol.isolate.artifacts,
            account.avilla.isolate.artifacts,
        )
        # 这里是为了能在 Context 层级进行修改

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

        def build_handler(artifact: tuple[BaseCollector, QueryHandlerPerform]) -> QueryHandler:
            async def handler(predicate: Callable[[str, str], bool] | str, previous: Selector | None = None):
                async with use_record(
                    {
                        "context": self,
                        "protocol": self.protocol,
                        "account": self.account,
                        "avilla": self.avilla,
                    },
                    artifact,
                ) as entity:
                    async for i in entity(predicate, previous):
                        yield i

            return handler

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
        # return await self[](resource)
        ...  # TODO

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
    def __getitem__(self, closure: Fn[Callable[P, Awaitable[R]]]) -> Callable[P, Awaitable[R]]:
        ...

    def __getitem__(self, closure: Selector | Fn[Callable[P, Awaitable[Any]]]) -> Any:
        if isinstance(closure, Selector):
            return ContextSelector(self, closure.pattern)

        async def run(*args: P.args, **kwargs: P.kwargs):
            return await run_fn(
                self.artifacts,
                {"context": self, "protocol": self.protocol, "account": self.account, "avilla": self.avilla},
                closure,
                *args,
                **kwargs,
            )

        return run

    def get_staff_components(self):
        return {
            "context": self,
            "protocol": self.protocol,
            "account": self.account,
            "avilla": self.avilla,
        }

    def get_staff_artifacts(self):
        return self.artifacts