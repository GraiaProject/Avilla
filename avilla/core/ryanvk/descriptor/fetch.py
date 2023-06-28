from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable
from typing import NoReturn as Never
from typing import TypeVar

from ..._vendor.dataclasses import dataclass
from .base import Fn

if TYPE_CHECKING:
    from avilla.core.resource import Resource

    from ...context import Context
    from ..collector import AvillaPerformTemplate, Collector


H = TypeVar("H", bound="AvillaPerformTemplate")
T = TypeVar("T")
X = TypeVar("X")


@dataclass(unsafe_hash=True)
class FetchImplement:
    resource: type[Resource]


class FetchFn(
    Fn[["Resource[T]"], Awaitable[T]],
):
    def __init__(self):
        ...

    def into(self, resource_type: type[Resource[X]]) -> FetchFn[X]:
        return self  # type: ignore[reportGeneralTypeIssues]

    def collect(self, collector: Collector, resource_type: type[Resource[T]]):
        def receive(entity: Callable[[H, Never], Awaitable[T]]):  # to accept all resource type
            collector.artifacts[FetchImplement(resource_type)] = (collector, entity)
            return entity

        return receive

    def get_execute_signature(self, runner: Context, resource: Resource) -> Any:
        return FetchImplement(type(Resource))

    def __repr__(self) -> str:
        return "<Fn#pull internal!>"
