from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Generic, TypeVar

from typing_extensions import Unpack

from ..._vendor.dataclasses import dataclass
from .target import TargetFn

if TYPE_CHECKING:
    from ...metadata import Metadata, MetadataRoute
    from ...selector import Selector
    from ..collector.context import ContextBasedPerformTemplate


M = TypeVar("M", bound="Metadata")
M1 = TypeVar("M1", bound="Metadata")


@dataclass(unsafe_hash=True)
class PullImplement(Generic[M]):
    route: type[M] | MetadataRoute[Unpack[tuple[Metadata, ...]], M]


class PullFn(
    TargetFn[["type[M] | MetadataRoute[Unpack[tuple[Metadata, ...]], M]"], Awaitable[M]],
):
    def __init__(self):
        ...

    def into(self, route: type[M1] | MetadataRoute[Unpack[tuple[Metadata, ...]], M1]) -> PullFn[M1]:
        return self  # type: ignore[reportGeneral]

    def get_collect_signature(
        self,
        entity: Callable[
            [ContextBasedPerformTemplate, "Selector", type[M] | MetadataRoute[Unpack[tuple[Metadata, ...]], M]],
            Awaitable[M],
        ],
        route: type[M] | MetadataRoute[Unpack[tuple[Metadata, ...]], M],
    ) -> Any:
        return PullImplement(route)

    def get_execute_signature(self, route: type[M] | MetadataRoute[Unpack[tuple[Metadata, ...]], M]):
        return PullImplement(route)

    def __repr__(self) -> str:
        return "<Fn#pull>"
