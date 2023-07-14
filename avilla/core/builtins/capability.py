from __future__ import annotations

from typing import TYPE_CHECKING

from ..ryanvk.capability import Capability
from ..ryanvk.descriptor.pull import PullFn
from ..ryanvk.descriptor.query import QuerySchema
from ..ryanvk.descriptor.target import TargetFn

if TYPE_CHECKING:
    from ..context import Context
    from ..selector import Selector


class CoreCapability(Capability):
    pull = PullFn()
    query = QuerySchema()

    @TargetFn
    async def get_context(self, *, via: Selector | None = None) -> Context:
        ...
