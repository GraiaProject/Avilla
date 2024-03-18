from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar, overload

from graia.ryanvk import BaseCollector

if TYPE_CHECKING:
    from typing_extensions import Unpack

    from avilla.core.metadata import Metadata, MetadataRoute
    from avilla.core.selector import Selector

T = TypeVar("T")
T1 = TypeVar("T1")

M = TypeVar("M", bound="Metadata")


Wrapper = Callable[[T], T]


class AvillaBaseCollector(BaseCollector):
    def __init__(self):
        super().__init__()

    @overload
    def pull(
        self, target: str, route: type[M]
    ) -> Callable[[Callable[[Any, Selector, type[M]], Awaitable[M]]], Callable[[Any, Selector, type[M]], Awaitable[M]]]:
        ...

    @overload
    def pull(
        self, target: str, route: MetadataRoute[Unpack[tuple[Any, ...]], M]
    ) -> Callable[[Callable[[Any, Selector, type[M]], Awaitable[M]]], Callable[[Any, Selector, type[M]], Awaitable[M]]]:
        ...

    def pull(self, target: str, route: ...) -> ...:
        from avilla.core.builtins.capability import CoreCapability

        return self.entity(CoreCapability.pull, target=target, route=route)

    def fetch(self, resource_type: type[T]) -> Wrapper[Callable[[Any, T], Awaitable[Any]]]:
        from avilla.core.builtins.capability import CoreCapability

        return self.entity(CoreCapability.fetch, resource=resource_type)  # type: ignore
