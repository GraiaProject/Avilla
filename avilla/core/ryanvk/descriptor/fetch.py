from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar

from ..._vendor.dataclasses import dataclass

if TYPE_CHECKING:
    from avilla.core.resource import Resource
    from ..collector.base import BaseCollector


T = TypeVar("T")
X = TypeVar("X")
R = TypeVar("R", bound="Resource")


@dataclass(unsafe_hash=True)
class FetchImplement:
    resource: type[Resource]


class Fetch:
    @classmethod
    def collect(
        cls,
        collector: BaseCollector,
        resource_type: type[Resource[T]],  # pyright: ignore[reportInvalidTypeVarUse]
    ):
        def receive(entity: Callable[[Any, R], Awaitable[T]]):  # to accept all resource type
            collector.artifacts[FetchImplement(resource_type)] = (collector, entity)
            return entity

        return receive
