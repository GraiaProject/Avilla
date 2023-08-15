from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
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
