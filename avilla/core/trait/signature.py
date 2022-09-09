from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, Hashable, TypeVar

if TYPE_CHECKING:
    from avilla.core.cell import Cell, CellOf
    from avilla.core.resource import Resource
    from avilla.core.trait import Fn
    from avilla.core.trait.extension import FnExtension


class ArtifactSignature:
    pass


@dataclass(unsafe_hash=True)
class Impl(ArtifactSignature):
    trait_call: Fn
    target: str | None
    path: type[Cell] | CellOf | None


@dataclass(unsafe_hash=True)
class Pull(ArtifactSignature):
    target: str | None
    path: type[Cell] | CellOf


@dataclass(unsafe_hash=True)
class ResourceFetch(ArtifactSignature):
    target: type[Resource]


@dataclass(unsafe_hash=True)
class Allow(ArtifactSignature):
    content: Hashable


@dataclass(unsafe_hash=True)
class CompleteRule(ArtifactSignature):
    relative: str


@dataclass(unsafe_hash=True)
class ImplDefaultTarget(ArtifactSignature):
    path: type[Cell] | CellOf | None
    trait_call: Fn


@dataclass(unsafe_hash=True)
class Query(ArtifactSignature):
    upper: str | None
    target: str

@dataclass(unsafe_hash=True)
class Check(ArtifactSignature):
    target: str


E = TypeVar("E", bound="FnExtension")

@dataclass(unsafe_hash=True)
class ExtensionImpl(ArtifactSignature, Generic[E]):
    ext: type[E]
