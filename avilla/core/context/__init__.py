from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypedDict, TypeVar, cast, overload

from typing_extensions import ParamSpec, Unpack

from avilla.core._runtime import cx_context
from avilla.core.account import BaseAccount
from avilla.core.metadata import Metadata, MetadataRoute
from avilla.core.platform import Land
from avilla.core.resource import Resource
from avilla.core.ryanvk import Fn
from avilla.core.ryanvk.staff import Staff
from avilla.core.selector import FollowsPredicater, Selectable, Selector
from avilla.core.utilles import classproperty

from ._roles import (
    ContextClientSelector,
    ContextEndpointSelector,
    ContextMedium,
    ContextRequestSelector,
    ContextSceneSelector,
    ContextSelfSelector,
)
from ._selector import ContextSelector

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
    self: ContextSelfSelector
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
        self.artifacts = [
            account.info.artifacts,
            account.info.protocol.artifacts,
            account.avilla.global_artifacts,
        ]
        # 这里是为了能在 Context 层级进行修改

        self.account = account

        self.client = ContextClientSelector.from_selector(self, client)
        self.endpoint = ContextEndpointSelector.from_selector(self, endpoint)
        self.scene = ContextSceneSelector.from_selector(self, scene)
        self.self = ContextSelfSelector.from_selector(self, selft)
        self.mediums = [ContextMedium(ContextSelector.from_selector(self, medium)) for medium in mediums or []]

        self.cache = {"meta": prelude_metadatas or {}}
        self.staff = Staff(self.get_staff_artifacts(), self.get_staff_components())

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

    def get_staff_components(self):
        return {
            "context": self,
            "protocol": self.protocol,
            "account": self.account,
            "avilla": self.avilla,
        }

    def get_staff_artifacts(self):
        return self.artifacts

    def query(self, pattern: str, **predicators: FollowsPredicater):
        return self.staff.query_entities(pattern, **predicators)

    async def fetch(self, resource: Resource[_T]) -> _T:
        return await self.staff.fetch_resource(resource)

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
            meta = cached[route]
            if flush:
                del cached[route]
            if not route.has_params():
                return cast("_MetadataT", meta)

        return await self.staff.pull_metadata(target, route)

    @overload
    def __getitem__(self, closure: Selector) -> ContextSelector:
        ...

    @overload
    def __getitem__(self, closure: Fn[P, R]) -> Callable[P, R]:
        ...

    def __getitem__(self, closure: Selector | Fn[P, Any]):
        if isinstance(closure, Selector):
            return ContextSelector(self, closure.pattern)

        def run(*args: P.args, **kwargs: P.kwargs):
            return self.staff.call_fn(closure, *args, **kwargs)

        return run

    def __staff_generic__(self, element_type: dict, event_type: dict):
        ...
