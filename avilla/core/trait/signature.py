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


@dataclass(unsafe_hash=True)
class Bounds(ArtifactSignature):
    bound: str | MetadataBound


@dataclass(unsafe_hash=True)
class Impl(ArtifactSignature):
    fn: Fn


@dataclass(unsafe_hash=True)
class Pull(ArtifactSignature):
    route: type[Metadata] | MetadataRoute


@dataclass(unsafe_hash=True)
class ResourceFetch(ArtifactSignature):
    target: type[Resource]


@dataclass(unsafe_hash=True)
class CompleteRule(ArtifactSignature):
    relative: str


@dataclass(unsafe_hash=True)
class Query(ArtifactSignature):
    upper: str | None
    target: str


@dataclass(unsafe_hash=True)
class VisibleConf(ArtifactSignature):
    checker: Callable[[Context], bool]


"""
E = TypeVar("E", bound="FnExtension")


@dataclass(unsafe_hash=True)
class ExtensionImpl(ArtifactSignature, Generic[E]):
    ext: type[E]
"""
