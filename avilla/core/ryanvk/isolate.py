from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ._runtime import processing_isolate

if TYPE_CHECKING:
    from .collector.base import PerformTemplate
    from .descriptor.target import LookupCollection


def _merge_lookup_collection(self: LookupCollection, other: LookupCollection):
    for key, branches in self.items():
        if (other_branches := other.pop(key, None)) is None:
            continue

        for header, branch in branches.items():
            if (other_branch := other_branches.pop(header, None)) is None:
                continue

            _merge_lookup_collection(branch.levels, other_branch.levels)
            branch.artifacts |= other_branch.artifacts

        branches |= other_branches

    self |= other


@dataclass
class Isolate:
    artifacts: dict[Any, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.artifacts["lookup_collections"] = [{}]

    def apply(self, ring3_class: type[PerformTemplate]):
        arti = ring3_class.__collector__.artifacts
        if "current_collection" in arti:
            _merge_lookup_collection(self.artifacts["lookup_collections"][0], arti.pop("current_collection"))
        self.artifacts.update(arti)

    @contextmanager
    def imports(self):
        token = processing_isolate.set(self)
        yield
        processing_isolate.reset(token)
