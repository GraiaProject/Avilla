from __future__ import annotations

from contextlib import AsyncExitStack, asynccontextmanager
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .fn import Fn, P, R
    from .perform import BasePerform


class StaffInstanceStore:
    staff: Staff
    exit_stack: AsyncExitStack
    instances: dict[type, Any]

    def __init__(self, staff: Staff) -> None:
        self.staff = staff
        self.exit_stack = AsyncExitStack()

    async def maintain(self, perform: BasePerform):
        await self.exit_stack.enter_async_context(perform.lifespan())

    @asynccontextmanager
    async def lifespan(self):
        async with self.exit_stack:
            yield self

        self.instances.clear()


class Staff:
    artifact_collections: list[dict[Any, Any]]
    components: dict[str, Any]

    def __init__(self, artifacts_collections: list[dict[Any, Any]], components: dict[str, Any]) -> None:
        self.artifact_collections = artifacts_collections
        self.components = components
        self.store = StaffInstanceStore(self)

    def call_fn(self, instance: BasePerform | None, fn: Fn[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        collector, entity = fn.get_artifact_record(self.artifact_collections, *args, **kwargs)
        if instance is None:
            instance = collector.cls()
            instance.__init_staff__(self)
        outbound = fn.get_outbound_callable(instance, entity)
        return outbound(*args, **kwargs)

    def inject(self, perform: BasePerform):
        perform.__init_staff__(self)
        self.artifact_collections.insert(0, perform.__collector__.artifacts)
