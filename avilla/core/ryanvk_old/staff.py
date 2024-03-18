from __future__ import annotations

from functools import reduce
from typing import TYPE_CHECKING, Any, Callable, ChainMap, overload

from typing_extensions import ParamSpec, TypeVar, Unpack

from avilla.core.builtins.capability import CoreCapability
from avilla.core.metadata import MetadataRoute
from avilla.core.selector import (
    FollowsPredicater,
    Selector,
    _FollowItem,
    _parse_follows,
)
from graia.ryanvk import BaseCollector
from graia.ryanvk import Staff as BaseStaff

from .descriptor.query import find_querier_steps, query_depth_generator

if TYPE_CHECKING:
    from avilla.core.metadata import Metadata
    from avilla.core.resource import Resource

    from .descriptor.query import QueryHandler, QueryHandlerPerform


T = TypeVar("T")
R = TypeVar("R", covariant=True)
M = TypeVar("M", bound="Metadata")
P = ParamSpec("P")
P1 = ParamSpec("P1")
N = TypeVar("N")
Co = TypeVar("Co", bound="BaseCollector")


class Staff(BaseStaff):
    """手杖与核心工艺 (Staff & Focus Craft)."""

    def get_context(self, target: Selector, *, via: Selector | None = None):
        return self.call_fn(CoreCapability.get_context, target, via=via)

    async def fetch_resource(self, resource: Resource[T]) -> T:
        return await self.get_fn_call(CoreCapability.fetch)(resource)

    @overload
    async def pull_metadata(
        self,
        target: Selector,
        route: type[M],
    ) -> M:
        ...

    @overload
    async def pull_metadata(
        self,
        target: Selector,
        route: MetadataRoute[Unpack[tuple[Any, ...]], T],
    ) -> T:
        ...

    async def pull_metadata(
        self,
        target: Selector,
        route: ...,
    ):
        return await self.call_fn(CoreCapability.pull, target, route)

    async def query_entities(self, pattern: str, **predicators: FollowsPredicater):
        items = _parse_follows(pattern, **predicators)
        artifact_map = ChainMap(*self.artifact_collections)
        steps = find_querier_steps(artifact_map, items)

        if steps is None:
            return

        def build_handler(artifact: tuple[BaseCollector, QueryHandlerPerform]) -> QueryHandler:
            async def handler(predicate: Callable[[str, str], bool] | str, previous: Selector | None = None):
                collector, entity = artifact

                def _get_instance(_staff: Staff, _cls: type[N]) -> N:
                    if _cls not in _staff.instances:
                        res = _staff.instances[_cls] = _cls(_staff)
                    else:
                        res = _staff.instances[_cls]

                    return res

                async for i in entity(_get_instance(self, collector.cls), predicate, previous):
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

        handlers = []
        for follow_item, query_record in steps:
            handlers.append((follow_item, build_handler(artifact_map[query_record])))

        r = reduce(
            lambda previous, current: query_depth_generator(current[1], build_predicate(current[0]), previous),
            handlers,
            None,
        )
        if TYPE_CHECKING:
            assert r is not None

        async for i in r:
            yield i
