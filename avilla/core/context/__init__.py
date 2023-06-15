from __future__ import annotations

from collections import ChainMap
from collections.abc import AsyncGenerator, Awaitable, Callable
from functools import cached_property, partial
from typing import Any, TypedDict, TypeVar, cast, overload

from typing_extensions import ParamSpec, TypeAlias, Unpack

from avilla.core._runtime import cx_context
from avilla.core.account import AbstractAccount
from avilla.core.metadata import Metadata, MetadataRoute
from avilla.core.resource import Resource
from avilla.core.ryanvk.capability import CoreCapability
from avilla.core.ryanvk.common.protocol import Executable
from avilla.core.ryanvk.common.runner import Runner as BaseRunner
from avilla.core.selector import Selectable, Selector
from avilla.core.trait import Trait
from avilla.core.trait.context import Artifacts
from avilla.core.trait.signature import Bounds, Pull, Query, ResourceFetch
from avilla.core.utilles import classproperty

from ._query import find_querier_steps as _find_querier_steps
from ._query import query_depth_generator as _query_depth_generator
from ._selector import (
    ContextClientSelector,
    ContextEndpointSelector,
    ContextMedium,
    ContextRequestSelector,
    ContextSceneSelector,
    ContextSelector,
)

P = ParamSpec("P")
R = TypeVar("R", covariant=True)
_T = TypeVar("_T")
_MetadataT = TypeVar("_MetadataT", bound=Metadata)
_DescribeT = TypeVar("_DescribeT", bound="type[Metadata] | MetadataRoute")
_TraitT = TypeVar("_TraitT", bound=Trait)

_Querier: TypeAlias = "Callable[[Context, Selector | None, Selector], AsyncGenerator[Selector, None]]"
_Describe: TypeAlias = "type[_MetadataT] | MetadataRoute[Unpack[tuple[Unpack[tuple[Any, ...]], _MetadataT]]]"


class ContextCache(TypedDict):
    meta: dict[Selector, dict[type[Metadata] | MetadataRoute, Metadata]]


class Context(BaseRunner):
    account: AbstractAccount

    client: ContextClientSelector
    endpoint: ContextEndpointSelector
    scene: ContextSceneSelector
    self: Selector
    mediums: list[ContextMedium]

    cache: ContextCache | dict[str, Any]

    def __init__(
        self,
        account: AbstractAccount,
        client: Selector,
        endpoint: Selector,
        scene: Selector,
        selft: Selector,
        mediums: list[Selector] | None = None,
        prelude_metadatas: dict[Selector, dict[type[Metadata] | MetadataRoute, Metadata]] | None = None,
    ) -> None:
        super().__init__()
        # TODO: Isolate-based Artifacts
        self.account = account

        self.client = ContextClientSelector.from_selector(self, client)
        self.endpoint = ContextEndpointSelector.from_selector(self, endpoint)
        self.scene = ContextSceneSelector.from_selector(self, scene)
        self.self = selft
        self.mediums = [ContextMedium(ContextSelector.from_selector(self, medium)) for medium in mediums or []]

        self.cache = {"meta": prelude_metadatas or {}}

    @property
    def protocol(self):
        return self.account.protocol

    @property
    def avilla(self):
        return self.protocol.avilla

    @property
    def land(self):
        return self.protocol.land

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

    async def query(self, pattern: str | Selector, with_land: bool = False):
        if isinstance(pattern, str):
            pattern = DynamicSelector.from_follows_pattern(pattern)
        else:
            pattern = pattern.as_dyn()

        querier_steps: list[Query] | None = _find_querier_steps(
            self._impl_artifacts, pattern.path if with_land else pattern.path_without_land
        )

        if querier_steps is None:
            raise NotImplementedError(f'cannot query "{pattern.path_without_land}" due to unknown step calc.')

        querier = cast("dict[Query, _Querier]", {i: self._impl_artifacts[i] for i in querier_steps})
        generators: list[AsyncGenerator[Selector, None]] = []

        past: list[str] = []
        for k, v in querier.items():
            past.append(k.target)
            pred = DynamicSelector({i: pattern.pattern[i] for i in past})
            current = _query_depth_generator(self, v, pred, generators[-1] if generators else None)
            generators.append(current)

        async for i in generators[-1]:
            if with_land:
                yield Selector({"land": self.land.name, **i.pattern})
            else:
                yield i

    async def fetch(self, resource: Resource[_T]) -> _T:
        return await self[CoreCapability.fetch](resource)

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

        return await self[CoreCapability.pull](target, route)

    @overload
    def __getitem__(self, closure: Selector) -> ContextSelector:
        ...

    @overload
    def __getitem__(self, closure: Executable[Context, P, R]) -> Callable[P, R]:
        ...

    def __getitem__(self, closure: Selector | Executable) -> Any:
        if isinstance(closure, Selector):
            return ContextSelector(self, closure.pattern)
        return partial(self.execute, closure)
