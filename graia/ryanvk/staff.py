from __future__ import annotations

from collections import ChainMap
from contextlib import AsyncExitStack, asynccontextmanager
from copy import copy
from typing import TYPE_CHECKING, Any, Callable, Protocol, TypeVar, overload

from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from .fn import Fn
    from .perform import BasePerform

P = ParamSpec("P")
R = TypeVar("R", covariant=True)


class Staff:
    artifact_collections: list[dict[Any, Any]]
    artifact_map: ChainMap[Any, Any]
    components: dict[str, Any]
    exit_stack: AsyncExitStack
    instances: dict[type, Any]

    def __init__(self, artifacts_collections: list[dict[Any, Any]], components: dict[str, Any]) -> None:
        self.artifact_collections = artifacts_collections
        self.artifact_map = ChainMap(*artifacts_collections)
        self.components = components
        self.exit_stack = AsyncExitStack()
        self.instances = {}

    def call_fn(self, fn: Fn[Callable[P, R]], *args: P.args, **kwargs: P.kwargs) -> R:
        collector, entity = fn.behavior.harvest_overload(self, fn, *args, **kwargs)
        instance = fn.behavior.get_instance(self, collector.cls)
        return entity(instance, *args, **kwargs)

    class PostInitShape(Protocol[P]):
        def __post_init__(self, *args: P.args, **kwargs: P.kwargs) -> Any:
            ...

    @overload
    def inject(self, perform_type: type[PostInitShape[P]], *args: P.args, **kwargs: P.kwargs) -> None:
        ...

    @overload
    def inject(self, perform_type: type[BasePerform]) -> None:
        ...

    def inject(self, perform_type: ..., *args, **kwargs):
        perform = perform_type(self)
        perform.__post_init__(*args, **kwargs)
        self.artifact_collections.insert(0, perform.__collector__.artifacts)

    async def maintain(self, perform: BasePerform):
        await self.exit_stack.enter_async_context(perform.lifespan())

    @asynccontextmanager
    async def lifespan(self):
        async with self.exit_stack:
            yield self

    def ext(self, components: dict[str, Any]):
        instance = copy(self)
        instance.components.update(components)
        return instance

    def get_fn_call(self, fn: Fn[Callable[P, R]]) -> Callable[P, R]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            collector, entity = fn.behavior.harvest_overload(self, fn, *args, **kwargs)
            instance = fn.behavior.get_instance(self, collector.cls)
            return entity(instance, *args, **kwargs)
        return wrapper
