from __future__ import annotations
from functools import reduce

from typing import TYPE_CHECKING, Any, AsyncGenerator, Awaitable, Callable, Protocol, TypeVar, overload
from typing_extensions import Unpack
from avilla.core.flywheel import Fn, FnCompose, SimpleOverload, TypeOverload, is_implemented
from avilla.core.ryanvk.target_overload import TargetOverload

from avilla.core.flywheel.typing import FnComposeCallReturnType, FnComposeCollectReturnType

from avilla.core.selector import _FollowItem, Selector, FollowsPredicater, _parse_follows

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

    if TYPE_CHECKING:

        def implement_sample(self, target: Selector, base: Selector | None) -> AsyncGenerator[Selector, None]:
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

    def call(self, pattern: str, **predicators: FollowsPredicater) -> FnComposeCallReturnType[AsyncGenerator[Selector, None]]:
        # TODO: 寻找 components (greedy?) -> 提取 predicators -> 组装 pipeline -> 返回 async generator.
        follows = _parse_follows(pattern, **predicators)
        components = []
        target: tuple[str, int, tuple] | None = "", 0, ()
        total = ".".join([i.name for i in follows])

        while target is not None:
            upper, start, history = target

            steps: list[_FollowItem] = []

            for frag in follows[start:]:
                steps.append(frag)
                backward = ".".join([i.name for i in steps])
                route = backward

                if upper:
                    route = f"{upper}.{route}"

                start += 1

                with self.harvest() as entities:
                    Selector.from_follows(upper)
                    if upper:
                        yield self.base.call(Selector.from_follows(upper))
                    else:
                        yield self.root.call(None)

                    yield self.dest.call(Selector.from_follows(backward))

                if TYPE_CHECKING:
                    components = [(steps, entities.first)]
                    continue

                if entities.ensured_result:
                    if route == total:
                        if len(components) > len(history) + 1:
                            components = [*history, entities.first]
                            break
                    else:
                        target = route, start, (*history, entities.first)

        # 先绑 predicator.
                        
        if not components:
            async def empty() -> AsyncGenerator[Selector, None]:
                if False:
                    yield
            return empty()

        def build_predicate_generator(moved_implement, moved_nodes):
            async def wrap_generator(target: Selector, base: Selector | None):
                async for object_ in moved_implement(target, base):
                    unmatched_flag = False

                    for node in moved_nodes:
                        if node.name in object_.pattern:
                            if node.literal is not None and node.literal != object_[node.name]:
                                unmatched_flag = True
                            elif node.predicate is not None and not node.predicate:
                                unmatched_flag = True

                    if unmatched_flag:
                        continue

                    yield object_

            return wrap_generator

        generator_origins = []
        backward = None

        for nodes, implement in components:
            generator = build_predicate_generator(implement, nodes)
            record = (generator, Selector({i.name: "" for i in nodes}))
            generator_origins.append(record)
            backward = nodes
        
        ... # TODO
