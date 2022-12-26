from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import Context
    from ..metadata import Metadata, MetadataBound, MetadataRoute
    from ..resource import Resource
    from ..trait import Fn


class ArtifactSignature:
    pass


@dataclass(eq=True, frozen=True)
class Bounds(ArtifactSignature):
    bound: str | MetadataBound


@dataclass(eq=True, frozen=True)
class Impl(ArtifactSignature):
    fn: Fn


@dataclass(eq=True, frozen=True)
class Pull(ArtifactSignature):
    route: type[Metadata] | MetadataRoute


@dataclass(eq=True, frozen=True)
class ResourceFetch(ArtifactSignature):
    target: type[Resource]


@dataclass(eq=True, frozen=True)
class CompleteRule(ArtifactSignature):
    relative: str


@dataclass(eq=True, frozen=True)
class Query(ArtifactSignature):
    upper: str | None
    target: str


@dataclass(eq=True, frozen=True)
class VisibleConf(ArtifactSignature):
    checker: Callable[[Context], bool]


@dataclass(eq=True, frozen=True)
class ContextSourceSign(ArtifactSignature):
    pattern: str


@dataclass(eq=True, frozen=True)
class EventParse(ArtifactSignature):
    event_type: str


@dataclass(eq=True, frozen=True)
class ElementParse(ArtifactSignature):
    element_type: str


"""
E = TypeVar("E", bound="FnExtension")


@dataclass(eq=True, frozen=True)
class ExtensionImpl(ArtifactSignature, Generic[E]):
    ext: type[E]
"""
