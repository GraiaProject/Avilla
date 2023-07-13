from __future__ import annotations

from functools import reduce
from typing import TYPE_CHECKING, Any, Awaitable, Callable, ChainMap, TypeVar

from typing_extensions import ParamSpec, Unpack

from avilla.core.builtins.capability import CoreCapability
from avilla.core.metadata import MetadataRoute
from avilla.core.ryanvk.descriptor.base import Fn
from avilla.core.selector import Selector
from graia.amnesia.message import Element, MessageChain

from ..selector import FollowsPredicater, _FollowItem, _parse_follows
from ..utilles import identity
from .descriptor.event import EventParserSign
from .descriptor.fetch import FetchImplement
from .descriptor.message.deserialize import MessageDeserializeSign
from .descriptor.message.serialize import MessageSerializeSign
from .descriptor.query import find_querier_steps, query_depth_generator
from .runner import run_fn, use_record

if TYPE_CHECKING:
    from avilla.core.event import AvillaEvent
    from avilla.core.metadata import Metadata
    from avilla.core.resource import Resource

    from .collector.base import BaseCollector
    from .descriptor.query import QueryHandler, QueryHandlerPerform
    from .protocol import SupportsArtifacts, SupportsStaff


T = TypeVar("T")
R = TypeVar("R", covariant=True)
_MetadataT = TypeVar("_MetadataT", bound="Metadata")
P = ParamSpec("P")


class Staff:
    components: dict[str, SupportsArtifacts]
    artifacts: ChainMap[Any, Any]

    def __init__(self, focus: SupportsStaff) -> None:
        self.components = focus.get_staff_components()
        self.artifacts = focus.get_staff_artifacts()

    async def call_fn(self, fn: Fn[Callable[P, Awaitable[R]]], *args: P.args, **kwargs: P.kwargs) -> R:
        return await run_fn(self.artifacts, self.components, fn, *args, **kwargs)

    async def parse_event(
        self,
        event_type: str,
        data: dict,
    ) -> AvillaEvent | None:
        sign = EventParserSign(event_type)
        if sign not in self.artifacts:
            return

        record: tuple[Any, Callable[[Any, dict], Awaitable[AvillaEvent | None]]] = self.artifacts[sign]

        async with use_record(self.components, record) as entity:
            return await entity(data)

    async def serialize_message(self, message: MessageChain) -> list[dict]:
        result: list[dict] = []
        for element in message.content:
            element_type = type(element)
            sign = MessageSerializeSign(element_type)
            if sign not in self.artifacts:
                raise NotImplementedError(f"Element {element_type} serialize is not supported")

            async with use_record(self.components, self.artifacts[sign]) as entity:
                result.append(await entity(element))
        return result

    async def deserialize_message(self, raw_elements: list[dict]) -> MessageChain:
        result: list[Element] = []
        for raw_element in raw_elements:
            element_type = raw_element["type"]
            sign = MessageDeserializeSign(element_type)
            if sign not in self.artifacts:
                raise NotImplementedError(f"Element {element_type} descrialize is not supported")

            async with use_record(self.components, self.artifacts[sign]) as entity:
                result.append(await entity(raw_element))
        return MessageChain(result)

    async def fetch_resource(self, resource: Resource[T]) -> T:
        sign = FetchImplement(type(resource))
        if sign not in self.artifacts:
            raise NotImplementedError(f"Resource {identity(resource)} fetch is not supported")

        record: tuple[Any, Callable[[Any, Resource[T]], Awaitable[T]]] = self.artifacts[sign]
        async with use_record(self.components, record) as entity:
            return await entity(resource)

    async def pull_metadata(
        self,
        target: Selector,
        route: type[_MetadataT] | MetadataRoute[Unpack[tuple[Any, ...]], _MetadataT],
    ) -> _MetadataT:
        return await run_fn(self.artifacts, self.components, CoreCapability.pull, target, route)

    async def query_entities(self, pattern: str, **predicators: FollowsPredicater):
        items = _parse_follows(pattern, **predicators)
        steps = find_querier_steps(self.artifacts, items)
        if steps is None:
            return

        def build_handler(artifact: tuple[BaseCollector, QueryHandlerPerform]) -> QueryHandler:
            async def handler(predicate: Callable[[str, str], bool] | str, previous: Selector | None = None):
                async with use_record(
                    self.components,
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
