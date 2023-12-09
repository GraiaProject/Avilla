from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Protocol, TypeVar, overload

from typing_extensions import Unpack

from avilla.core.metadata import Metadata, MetadataRoute
from avilla.core.resource import Resource, T
from avilla.core.ryanvk.descriptor.query import QuerySchema
from avilla.core.ryanvk.overload.target import TargetOverload
from graia.ryanvk.collector import BaseCollector
from graia.ryanvk.fn import Fn, FnCompose
from graia.ryanvk.overloads import SimpleOverload, TypeOverload
from graia.ryanvk.typing import FnComposeCallReturnType, FnComposeCollectReturnType

if TYPE_CHECKING:
    from avilla.core.context import Context
    from avilla.core.selector import Selector


M = TypeVar("M", bound=Metadata)

MR = TypeVar("MR", bound=Metadata, covariant=True)
RQ = TypeVar("RQ", bound=Resource, contravariant=True)
RQ1 = TypeVar("RQ1", bound=Resource, contravariant=True)
RR = TypeVar("RR", bound=Resource, covariant=True)
R = TypeVar("R")
RT = TypeVar("RT", bound=Resource)


class FetchImplShape(Protocol[RT, RR]):
    def __call__(self: FetchImplShape[RT, Resource[R]], resource: RT) -> R:
        ...


class CoreCapability((m := BaseCollector())._):
    #query = QuerySchema()

    @m.entity
    @Fn.compose
    class get_context(FnCompose):
        target = TargetOverload().as_agent()
        via = TargetOverload().as_agent()
        via_none = SimpleOverload().as_agent()
        
        class CollectShape(Protocol):
            def __call__(self, target: Selector, *, via: Selector | None):
                ...

        def collect(self, implement: CollectShape, target: str, via: str | None = None):
            yield self.target.collect(target)

            if via is None:
                yield self.via_none.collect(None)
            else:
                yield self.via.collect(via)

        def call(self, target: Selector, *, via: Selector | None = None) -> FnComposeCallReturnType[Any]:
            with self.harvest() as entities:
                yield self.target.call(target)
                if via is None:
                    yield self.via_none.call(None)
                else:
                    yield self.via.call(via)
            
            return entities.first(target, via=via)  # type: ignore

    @m.entity
    @Fn.compose
    class pull(FnCompose):
        target = TargetOverload().as_agent()
        route = SimpleOverload().as_agent()

        class CollectShape(Protocol[MR]):
            def __call__(self, target: Selector) -> MR:
                ...
        
        def collect(self, implement: CollectShape[M], target: str, route: type[M] | MetadataRoute[Unpack[tuple[Any, ...]], M]) -> FnComposeCollectReturnType:
            yield self.target.collect(target)
            yield self.route.collect(route)
        
        def call(self, target: Selector, route: type[M] | MetadataRoute[Unpack[tuple[Any, ...]], M]) -> FnComposeCallReturnType[M]:
            with self.harvest() as entities:
                yield self.target.call(target)
                yield self.route.call(route)

            return entities.first(target)

    @m.entity
    @Fn.compose
    class fetch(FnCompose):
        resource_type = TypeOverload().as_agent()

        def collect(self, implement: FetchImplShape[RQ, RQ], resource_type: type[RQ]) -> FnComposeCollectReturnType:
            yield self.resource_type.collect(resource_type)
        
        def call(self, resource: Resource[T]) -> FnComposeCallReturnType[T]:
            with self.harvest() as entities:
                yield self.resource_type.call(resource)
            
            return entities.first(resource)

    # TODO: query   
