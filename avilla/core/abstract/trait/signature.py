from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, Hashable, TypeVar

if TYPE_CHECKING:
    from ..metadata import Metadata, MetadataBound, MetadataRoute
    from ..resource import Resource
    from ..trait import Fn, Trait


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


"""
E = TypeVar("E", bound="FnExtension")


@dataclass(unsafe_hash=True)
class ExtensionImpl(ArtifactSignature, Generic[E]):
    ext: type[E]
"""
