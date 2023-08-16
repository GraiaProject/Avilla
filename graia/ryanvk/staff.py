from __future__ import annotations

from contextlib import AsyncExitStack, asynccontextmanager
from copy import copy
from typing import TYPE_CHECKING, Any, Callable, Protocol, TypeVar, overload

from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from .fn import Fn
    from .perform import BasePerform
    from .typing import P1, OutboundCompatible

P = ParamSpec("P")
R = TypeVar("R", covariant=True)


class Staff:
    artifact_collections: list[dict[Any, Any]]
    components: dict[str, Any]
    exit_stack: AsyncExitStack
    instances: dict[type, Any]

    def __init__(self, artifacts_collections: list[dict[Any, Any]], components: dict[str, Any]) -> None:
        self.artifact_collections = artifacts_collections
        self.components = components
        self.exit_stack = AsyncExitStack()
        self.instances = {}

    def get_outbound(
        self,
        schema: OutboundCompatible[P, R, P1],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Callable[P1, R]:
        instance, entity = schema.get_artifact_record(self.artifact_collections, *args, **kwargs).unwrap(self)
        return schema.get_outbound_callable(instance, entity)

    def call_fn(self, fn: Fn[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        outbound = self.get_outbound(fn, *args, **kwargs)
        return outbound(*args, **kwargs)

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