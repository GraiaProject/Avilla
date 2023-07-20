from __future__ import annotations

from functools import reduce
from typing import TYPE_CHECKING, Any, Awaitable, Callable, ChainMap, Generic, overload

from typing_extensions import ParamSpec, TypeVar, Unpack

from avilla.core.builtins.capability import CoreCapability
from avilla.core.metadata import MetadataRoute
from avilla.core.ryanvk.descriptor.base import Fn
from avilla.core.selector import FollowsPredicater, Selector, _FollowItem, _parse_follows
from avilla.core.utilles import identity
from graia.amnesia.message import Element, MessageChain

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
M = TypeVar("M", bound="Metadata")
P = ParamSpec("P")

VnEventRaw = TypeVar("VnEventRaw", default=dict, infer_variance=True)
VnElementRaw = TypeVar("VnElementRaw", default=dict, infer_variance=True)


class Staff(Generic[VnElementRaw, VnEventRaw]):
    """手杖与核心工艺 (Staff & Focus Craft)."""

    components: dict[str, SupportsArtifacts]
    artifacts: ChainMap[Any, Any]

    def __init__(self, components: dict[str, SupportsArtifacts], artifacts: ChainMap[Any, Any]):
        self.components = components
        self.artifacts = artifacts

    @classmethod
    def focus(
        cls,
        focus: SupportsStaff[VnElementRaw, VnEventRaw],
        *,
        element_typer: Callable[[VnElementRaw], Any] | None = None,
    ):
        self = super().__new__(cls)
        self.components = focus.get_staff_components()
        self.artifacts = focus.get_staff_artifacts()
        if element_typer is not None:
            self.get_element_type = element_typer  # type: ignore
        return self

    def x(self, components: dict[str, SupportsArtifacts]):
        return type(self)({**self.components, **components}, self.artifacts)

    def get_element_type(self, raw_element: VnElementRaw):
        return raw_element["type"]  # type: ignore

    async def get_context(self, target: Selector, *, via: Selector | None = None):
        return await self.call_fn(CoreCapability.get_context, target, via=via)

    async def call_fn(self, fn: Fn[Callable[P, Awaitable[R]]], *args: P.args, **kwargs: P.kwargs) -> R:
        return await run_fn(self.artifacts, self.components, fn, *args, **kwargs)

    async def parse_event(
        self,
        event_type: str,
        data: VnEventRaw,
    ) -> AvillaEvent | None:
        sign = EventParserSign(event_type)
        if sign not in self.artifacts:
            return

        record: tuple[Any, Callable[[Any, VnEventRaw], Awaitable[AvillaEvent | None]]] = self.artifacts[sign]

        async with use_record(self.components, record) as entity:
            return await entity(data)

    async def serialize_message(self, message: MessageChain) -> list[VnElementRaw]:
        result: list[VnElementRaw] = []
        for element in message.content:
            element_type = type(element)
            sign = MessageSerializeSign(element_type)
            if sign not in self.artifacts:
                raise NotImplementedError(f"Element {element_type} serialize is not supported")

            async with use_record(self.components, self.artifacts[sign]) as entity:
                result.append(await entity(element))
        return result

    async def deserialize_message(self, raw_elements: list[VnElementRaw]) -> MessageChain:
        result: list[Element] = []
        for raw_element in raw_elements:
            element_type = self.get_element_type(raw_element)
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
        return await run_fn(self.artifacts, self.components, CoreCapability.pull, target, route)

    async def query_entities(self, pattern: str, **predicators: FollowsPredicater):
        items = _parse_follows(pattern, **predicators)
        steps = find_querier_steps(self.artifacts, items)

        if steps is None:
            return

        def build_handler(artifact: tuple[BaseCollector, QueryHandlerPerform]) -> QueryHandler:
            async def handler(predicate: Callable[[str, str], bool] | str, previous: Selector | None = None):
                async with use_record(self.components, artifact) as entity:
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

        handlers = []
        for follow_item, query_record in steps:
            handlers.append((follow_item, build_handler(self.artifacts[query_record])))

        r = reduce(
            lambda previous, current: query_depth_generator(current[1], build_predicate(current[0]), previous),
            handlers,
            None,
        )
        if TYPE_CHECKING:
            assert r is not None

        async for i in r:
            yield i
