from __future__ import annotations

from functools import reduce
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    ChainMap,
    Generic,
    Literal,
    overload,
)

from typing_extensions import ParamSpec, TypeVar, Unpack

from avilla.core.builtins.capability import CoreCapability
from avilla.core.metadata import MetadataRoute
from avilla.core.selector import FollowsPredicater, Selector, _FollowItem, _parse_follows
from avilla.core.utilles import identity
from graia.amnesia.message import Element, MessageChain
from graia.ryanvk import BaseCollector, RecordTwin
from graia.ryanvk import Staff as BaseStaff

from .descriptor.event import EventParserSign
from .descriptor.fetch import FetchImplement
from .descriptor.message.deserialize import MessageDeserializeSign
from .descriptor.message.serialize import MessageSerializeSign
from .descriptor.query import find_querier_steps, query_depth_generator

if TYPE_CHECKING:
    from avilla.core.event import AvillaEvent
    from avilla.core.metadata import Metadata
    from avilla.core.resource import Resource

    from .descriptor.query import QueryHandler, QueryHandlerPerform
    from .protocol import SupportsStaff


T = TypeVar("T")
R = TypeVar("R", covariant=True)
M = TypeVar("M", bound="Metadata")
P = ParamSpec("P")
P1 = ParamSpec("P1")
Co = TypeVar("Co", bound="BaseCollector")

VnEventRaw = TypeVar("VnEventRaw", default=dict, infer_variance=True)
VnElementRaw = TypeVar("VnElementRaw", default=dict, infer_variance=True)


class Staff(BaseStaff, Generic[VnElementRaw, VnEventRaw]):
    """手杖与核心工艺 (Staff & Focus Craft)."""

    @classmethod
    def focus(
        cls,
        focus: SupportsStaff[VnElementRaw, VnEventRaw],
        *,
        element_typer: Callable[[VnElementRaw], Any] | None = None,
    ):
        self = super().__new__(cls)
        self.__init__(
            focus.get_staff_artifacts(),
            focus.get_staff_components(),
        )
        if element_typer is not None:
            self.get_element_type = element_typer  # type: ignore
        return self

    # [= Avilla-only =]

    def get_element_type(self, raw_element: VnElementRaw):
        return raw_element["type"]  # type: ignore

    def get_context(self, target: Selector, *, via: Selector | None = None):
        return self.call_fn(CoreCapability.get_context, target, via=via)

    async def parse_event(
        self,
        event_type: str,
        data: VnEventRaw,
    ) -> AvillaEvent | Literal["non-implemented"] | None:
        sign = EventParserSign(event_type)
        artifact_map = ChainMap(*self.artifact_collections)
        if sign not in artifact_map:
            return "non-implemented"

        record: RecordTwin[Any, Callable[[Any, VnEventRaw], Awaitable[AvillaEvent | None]]] = artifact_map[sign]

        instance, entity = record.unwrap(self)
        return await entity(instance, data)

    async def serialize_message(self, message: MessageChain) -> list[VnElementRaw]:
        result: list[VnElementRaw] = []
        artifact_map = ChainMap(*self.artifact_collections)
        for element in message.content:
            element_type = type(element)
            sign = MessageSerializeSign(element_type)
            if sign not in artifact_map:
                raise NotImplementedError(f"Element {element_type} serialize is not supported")

            record = artifact_map[sign]
            instance, entity = record.unwrap(self)
            result.append(await entity(instance, element))

        return result

    async def deserialize_message(self, raw_elements: list[VnElementRaw]) -> MessageChain:
        result: list[Element] = []
        artifact_map = ChainMap(*self.artifact_collections)
        for raw_element in raw_elements:
            element_type = self.get_element_type(raw_element)
            sign = MessageDeserializeSign(element_type)
            if sign not in artifact_map:
                raise NotImplementedError(f"Element {element_type} deserialize is not supported: {raw_element}")

            record = artifact_map[sign]
            instance, entity = record.unwrap(self)
            result.append(await entity(instance, raw_element))

        return MessageChain(result)

    async def fetch_resource(self, resource: Resource[T]) -> T:
        sign = FetchImplement(type(resource))
        artifact_map = ChainMap(*self.artifact_collections)
        if sign not in artifact_map:
            raise NotImplementedError(f"Resource {identity(resource)} fetch is not supported")

        record: RecordTwin[Any, Callable[[Any, Resource[T]], Awaitable[T]]] = artifact_map[sign]

        instance, entity = record.unwrap(self)
        return await entity(instance, resource)

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

        def build_handler(artifact: RecordTwin[BaseCollector, QueryHandlerPerform]) -> QueryHandler:
            async def handler(predicate: Callable[[str, str], bool] | str, previous: Selector | None = None):
                instance, entity = artifact.unwrap(self)
                async for i in entity(instance, predicate, previous):
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
