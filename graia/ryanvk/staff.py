from __future__ import annotations

from contextlib import AsyncExitStack, asynccontextmanager
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .fn import Fn, P, R
    from .perform import BasePerform
    from .typing import P1, C, OutboundCompatible


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

    def extract_record(self, record: tuple[C, Any]):
        collector, entity = record
        instance = self.instances.get(collector.cls)
        if instance is None:
            raise TypeError(f"instance not found for {collector.cls}")
        return instance, entity

    def extract_outbound(
        self,
        schema: OutboundCompatible[P, R, P1],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Callable[P1, R]:
        instance, entity = self.extract_record(schema.get_artifact_record(self.artifact_collections, *args, **kwargs))
        return schema.get_outbound_callable(instance, entity)

    def call_fn(self, fn: Fn[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        outbound = self.extract_outbound(fn, *args, **kwargs)
        return outbound(*args, **kwargs)

    def inject(self, perform: BasePerform):
        perform.__init_staff__(self)
        self.artifact_collections.insert(0, perform.__collector__.artifacts)

    async def maintain(self, perform: BasePerform):
        await self.exit_stack.enter_async_context(perform.lifespan())

    @asynccontextmanager
    async def lifespan(self):
        async with self.exit_stack:
            yield self
