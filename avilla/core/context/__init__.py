from __future__ import annotations

from collections import ChainMap
from collections.abc import AsyncGenerator, Awaitable, Callable
from functools import cached_property
from typing import Any, TypedDict, TypeVar, cast, overload

from graia.amnesia.message import __message_chain_class__
from typing_extensions import TypeAlias, Unpack

from avilla.core._runtime import ctx_context
from avilla.core.account import AbstractAccount
from avilla.core.metadata import Metadata, MetadataBound, MetadataOf, MetadataRoute
from avilla.core.resource import Resource
from avilla.core.selector import Selectable, Selector
from avilla.core.trait import Trait
from avilla.core.trait.context import Artifacts
from avilla.core.trait.signature import Bounds, Pull, Query, ResourceFetch, VisibleConf
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
    ContextWrappedMetadataOf,
)

_T = TypeVar("_T")
_MetadataT = TypeVar("_MetadataT", bound=Metadata)
_DescribeT = TypeVar("_DescribeT", bound="type[Metadata] | MetadataRoute")
_TraitT = TypeVar("_TraitT", bound=Trait)

_Querier: TypeAlias = Callable[["Context", Selector | None, Selector], AsyncGenerator[Selector, None]]
_Describe: TypeAlias = type[_MetadataT] | MetadataRoute[Unpack[tuple[Unpack[tuple[Any, ...]], _MetadataT]]]


class ContextCache(TypedDict):
    meta: dict[Selector, dict[type[Metadata] | MetadataRoute, Metadata]]


class Context:
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

    @cached_property
    def _impl_artifacts(self) -> Artifacts:
        m = [
            self.protocol.implementations,
            *[v for k, v in self.protocol.implementations.items() if isinstance(k, VisibleConf) and k.checker(self)],
        ]
        return ChainMap(*m[::-1], self.avilla.global_artifacts)

    @property
    def request(self) -> ContextRequestSelector:
        return self.endpoint.expects_request()

    @property
    def is_resource(self) -> bool:
        return any(isinstance(i, Resource) for i in self.cache["meta"].get(self.endpoint, {}).values())

    def _collect_metadatas(self, target: Selector | Selectable, *metadatas: Metadata):
        scope = self.cache["meta"].setdefault(target.to_selector(), {})
        scope.update({type(i): i for i in metadatas})

    def _get_entity_bound_scope(self, target: Selector):
        return next(
            (
                v
                for k, v in self._impl_artifacts.items()
                if isinstance(k, Bounds) and isinstance(k.bound, str) and target.follows(k.bound)
            ),
            {},
        )

    def _get_metadata_bound_scope(self, reference: MetadataOf):
        return next(
            (
                v
                for k, v in self._impl_artifacts.items()
                if isinstance(k, Bounds)
                and isinstance(k.bound, MetadataBound)
                and reference.target.follows(k.bound.target)
                and reference.describe == k.bound.describe
            ),
            {},
        )

    """
    @property
    def _ext_handler(self):
        return ExtensionHandler(self)
    """

    @classproperty
    @classmethod
    def current(cls) -> Context:
        return ctx_context.get()

    async def query(self, pattern: Selector, with_land: bool = False):
        querier_steps: list[Query] | None = _find_querier_steps(
            self._impl_artifacts, pattern.path if with_land else pattern.path_without_land
        )

        if querier_steps is None:
            raise NotImplementedError(f'cannot query "{pattern.path_without_land}" due to unknown step calc.')

        querier = cast("dict[Query, _Querier]", {i: self._impl_artifacts[i] for i in querier_steps})
        generators: list[AsyncGenerator[Selector, None]] = []

        past = []
        for k, v in querier.items():
            past.append(k.target)
            pred = pattern.mixin(".".join(past))
            current = _query_depth_generator(self, v, pred, generators[-1] if generators else None)
            generators.append(current)

        async for i in generators[-1]:
            if with_land:
                yield Selector({"land": self.land.name, **i.pattern})
            else:
                yield i

    # TODO: GraiaProject/Avilla#66
    # TODO: redesign Context.complete

    """
    def complete(self, selector: Selector, with_land: bool = False):
        output_rule = self._impl_artifacts.get(CompleteRule(selector.path_without_land))
        if output_rule is not None:
            output_rule = cast(str, output_rule)
            selector = Selector().mixin(output_rule, selector, self.endpoint, self.scene)
        if with_land and list(selector.pattern.keys())[0] != "land":
            selector.pattern = {"land": self.land.name, **selector.pattern}
        return selector
    """

    async def fetch(self, resource: Resource[_T]) -> _T:
        fetcher = self._impl_artifacts.get(ResourceFetch(type(resource)))
        if fetcher is None:
            raise NotImplementedError(
                f'cannot fetch "{resource}" because no available fetch implement found in "{self.protocol.__class__.__name__}"'
            )
        return await fetcher(self, resource)

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

        pull_implement = self._impl_artifacts.get(Bounds(target.path_without_land), {}).get(Pull(route))
        if pull_implement is None:
            raise NotImplementedError(
                f'cannot pull "{route}"'
                + (f' for "{target.path_without_land}"' if target is not None else "")
                + f' because no available implement found in "{self.protocol.__class__.__name__}"'
            )
        pull_implement = cast(Callable[[Context, "Selector | None"], Awaitable[_MetadataT]], pull_implement)
        result = await pull_implement(self, target)
        if target is not None and not route.has_params():
            cached = self.cache["meta"].setdefault(target, {})
            cached[route] = result
        return result

    @overload
    def wrap(self, closure: Selector) -> ContextSelector:
        ...

    @overload
    def wrap(self, closure: MetadataOf[_Describe]) -> ContextWrappedMetadataOf[_Describe]:
        ...

    @overload
    def wrap(self, closure: type[_TraitT]) -> type[_TraitT]:
        ...

    def wrap(
        self,
        closure: Selector | MetadataOf[_DescribeT] | type[_TraitT],
    ) -> ContextSelector | ContextWrappedMetadataOf[_Describe] | type[_TraitT]:
        if isinstance(closure, type) and issubclass(closure, Trait):
            return type(closure.__name__, (closure,), {"context": self})  # type: ignore
        elif isinstance(closure, Selector):
            return ContextSelector.from_selector(self, closure)
        elif isinstance(closure, MetadataOf):
            return ContextWrappedMetadataOf(closure.target, closure.describe, self)

        raise TypeError(f"cannot wrap {closure!r}")
