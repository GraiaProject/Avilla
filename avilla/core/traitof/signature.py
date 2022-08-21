from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Hashable

if TYPE_CHECKING:
    from avilla.core.cell import Cell, CellOf
    from avilla.core.traitof import TraitCall


class ArtifactSignature:
    pass


@dataclass(unsafe_hash=True)
class Impl(ArtifactSignature):
    trait_call: TraitCall
    target: str | None
    path: type[Cell] | CellOf | None


@dataclass(unsafe_hash=True)
class Pull(ArtifactSignature):
    target: str | None
    path: type[Cell] | CellOf


@dataclass(unsafe_hash=True)
class ResourceFetch(ArtifactSignature):
    target: str


@dataclass(unsafe_hash=True)
class Allow(ArtifactSignature):
    content: Hashable


@dataclass(unsafe_hash=True)
class CompleteRule(ArtifactSignature):
    relative: str


@dataclass(unsafe_hash=True)
class ImplDefaultTarget(ArtifactSignature):
    path: type[Cell] | CellOf | None
    trait_call: TraitCall


@dataclass(unsafe_hash=True)
class Query(ArtifactSignature):
    path: str


@dataclass(unsafe_hash=True)
class EventKeyGetter(ArtifactSignature):
    ...
