from __future__ import annotations

from collections import ChainMap
from contextlib import asynccontextmanager
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Protocol,
    TypeVar,
)

from typing_extensions import Concatenate, ParamSpec

if TYPE_CHECKING:
    # from .descriptor.base import VnCollector
    from .collector.base import BaseCollector
    from .descriptor.base import Fn


Co = TypeVar("Co", bound="BaseCollector")
T = TypeVar("T", covariant=True)
R = TypeVar("R", covariant=True)
P = ParamSpec("P")


class ArtifactSchema(Protocol[P, T]):
    def get_artifact_record(
        self,
        collection: ChainMap[Any, Any],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> tuple[Any, T]:
        ...


@asynccontextmanager
async def use_artifact(
    artifact_collection: ChainMap[str, Any],
    components: dict[str, Any],
    schema: ArtifactSchema[P, Callable[Concatenate[Any, P], R]],
    *args: P.args,
    **kwargs: P.kwargs,
) -> AsyncGenerator[Callable[P, R], None]:
    collector, entity = schema.get_artifact_record(artifact_collection, *args, **kwargs)
    async with collector.cls(components).run_with_lifespan() as instance:

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return entity(instance, *args, **kwargs)

        yield wrapper


@asynccontextmanager
async def use_record(
    components: dict[str, Any],
    record: tuple[Co, Callable[Concatenate[Any, P], R]],
) -> AsyncGenerator[Callable[P, R], None]:
    collector, entity = record
    async with collector.cls(components).run_with_lifespan() as instance:

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return entity(instance, *args, **kwargs)

        yield wrapper


async def run_fn(
    artifact_collection: ChainMap[str, Any],
    components: dict[str, Any],
    schema: Fn[Callable[P, Awaitable[R]]],
    *args: P.args,
    **kwargs: P.kwargs,
) -> R:
    async with use_artifact(artifact_collection, components, schema, *args, **kwargs) as entity:
        return await entity(*args, **kwargs)
