from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from typing_extensions import Unpack

from avilla.core.metadata import Metadata, MetadataRoute
from avilla.core.resource import Resource, T
from avilla.core.ryanvk.descriptor.query import QuerySchema
from avilla.core.ryanvk.overload.metadata import MetadataOverload
from avilla.core.ryanvk.overload.target import TargetOverload
from graia.ryanvk.capability import Capability
from graia.ryanvk.fn import Fn
from graia.ryanvk.overload import NoneOverload, TypeOverload

if TYPE_CHECKING:
    from avilla.core.context import Context
    from avilla.core.selector import Selector


M = TypeVar("M", bound=Metadata)


class CoreCapability(Capability):
    query = QuerySchema()

    @Fn.complex(
        {
            TargetOverload(): ["target"],
            NoneOverload(TargetOverload(), default_factory=lambda _: None): ["via"],
        }
    )
    def get_context(self, target: Selector, *, via: Selector | None = None) -> Context:
        ...

    @Fn.complex({TargetOverload(): ["target"], MetadataOverload(): ["route"]})
    async def pull(self, target: Selector, route: type[M] | MetadataRoute[Unpack[tuple[Any, ...]], M]) -> Any:
        ...

    @Fn.complex({TypeOverload(): ["resource"]})
    async def fetch(self, resource: Resource[T]) -> T:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    def channel(self, target: Selector) -> str:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    def guild(self, target: Selector) -> str:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    def user(self, target: Selector) -> str:
        ...
