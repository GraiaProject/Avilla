from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, Hashable, TypeVar

if TYPE_CHECKING:
    from avilla.core.metadata import Metadata, MetadataRoute, MetadataBound
    from avilla.core.resource import Resource
    from avilla.core.trait import Fn, Trait
    from avilla.core.trait.extension import FnExtension


class ArtifactSignature:
    pass


@dataclass(unsafe_hash=True)
class Override(ArtifactSignature):
    client: str | None = None
    endpoint: str | None = None
    scene: str | None = None


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


E = TypeVar("E", bound="FnExtension")


@dataclass(unsafe_hash=True)
class ExtensionImpl(ArtifactSignature, Generic[E]):
    ext: type[E]
