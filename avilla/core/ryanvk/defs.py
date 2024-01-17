from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncGenerator, Awaitable, Callable, Protocol, TypeVar, overload
from typing_extensions import Unpack
from avilla.core.flywheel import Fn, FnCompose, SimpleOverload, TypeOverload
from avilla.core.ryanvk.target_overload import TargetOverload

from avilla.core.flywheel.typing import FnComposeCallReturnType, FnComposeCollectReturnType

from avilla.core.selector import Selector, FollowsPredicater

if TYPE_CHECKING:
    from avilla.core.context import Context
    from avilla.core.resource import Resource
    from avilla.core.metadata import Metadata, MetadataRoute


@Fn.compose
class get_context(FnCompose):
    target = TargetOverload().as_agent()
    novia = SimpleOverload().as_agent()
    via = TargetOverload().as_agent()

    class ImplementShapeNoVia(Protocol):
        def __call__(self, target: Selector, *, via: None) -> Context:
            ...

    class ImplementShapeVia(Protocol):
        def __call__(self, target: Selector, *, via: Selector) -> Context:
            ...

    @overload
    def collect(self, implement: ImplementShapeNoVia, target: str, via: None = None):
        ...

    @overload
    def collect(self, implement: ImplementShapeVia, target: str, via: str):
        ...

    def collect(self, implement: ..., target: str, via: str | None = None):
        yield self.target.collect((target, {}))

        if via is None:
            yield self.novia.collect(None)
        else:
            yield self.via.collect((via, {}))

    if TYPE_CHECKING:

        def implement_sample(self, target: Selector, via: Selector | None) -> Context:
            ...

    def call(self, target: Selector, *, via: Selector | None = None):
        with self.harvest() as entities:
            yield self.target.call(target)

            if via is None:
                yield self.novia.call(None)
            else:
                yield self.via.call(via)

        return entities.first(target, via=via)


# TODO: Refactoring Metadata

T = TypeVar("T")
R1 = TypeVar("R1", covariant=True)
R2 = TypeVar("R2", covariant=True)
ResT = TypeVar("ResT", bound=Resource)
M = TypeVar("M", bound="Metadata")
MR = TypeVar("MR", bound="Metadata", covariant=True)


@Fn.compose
class pull(FnCompose):
    target = TargetOverload().as_agent()
    metadata = SimpleOverload().as_agent()

    class ImplementShape(Protocol[MR]):
        async def __call__(self, target: Selector) -> MR:
            ...

    def collect(
        self,
        implement: ImplementShape[M],
        target: str,
        route: type[M] | MetadataRoute[Unpack[tuple[Any, ...]], M],
    ):
        yield self.target.collect((target, {}))
        yield self.metadata.collect(route)

    def call(
        self,
        target: Selector,
        route: type[M] | MetadataRoute[Unpack[tuple[Any, ...]], M],
    ) -> FnComposeCallReturnType[Awaitable[M]]:
        with self.harvest() as entities:
            yield self.target.call(target)
            yield self.metadata.call(route)

        return entities.first(target)


class FetchImplementShape(Protocol[R1, ResT]):
    async def __call__(self: FetchImplementShape[Resource[T], ResT], resource: ResT) -> T:
        ...


@Fn.compose
class fetch(FnCompose):
    type = TypeOverload().as_agent()

    def collect(self, implement: FetchImplementShape[ResT, ResT], resource_type: type[ResT]):
        yield self.type.collect(resource_type)

    def call(self, resource: Resource[T]) -> FnComposeCallReturnType[Awaitable[T]]:
        with self.harvest() as entities:
            yield self.type.call(resource)

        return entities.first(resource)


@Fn.compose
class query(FnCompose):
    base = TargetOverload().as_agent()
    root = SimpleOverload().as_agent()
    dest = TargetOverload().as_agent()

    class ImplementFromRoot(Protocol):
        def __call__(self, target: Selector, base: None) -> AsyncGenerator[Selector, None]:
            ...
    
    class ImplementFromBase(Protocol):
        def __call__(self, target: Selector, base: Selector) -> AsyncGenerator[Selector, None]:
            ...

    @overload
    def collect(self, implement: ImplementFromRoot, target: str, base: None = None):
        ...
    
    @overload
    def collect(self, implement: ImplementFromBase, target: str, base: str):
        ...
    
    def collect(self, implement: ..., target: str, base: str | None = None):
        yield self.dest.collect((target, {}))
        if base is None:
            yield self.root.collect(None)
        else:
            yield self.base.collect((base, {}))

    def call(self, pattern: str, **predicators: FollowsPredicater):
        # TODO