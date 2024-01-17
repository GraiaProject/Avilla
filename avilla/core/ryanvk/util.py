from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .target_overload import LookupCollection


def merge_lookup_collection(self: LookupCollection, other: LookupCollection):
    for key, branches in self.items():
        if (other_branches := other.pop(key, None)) is None:
            continue

        for header, branch in branches.items():
            if (other_branch := other_branches.pop(header, None)) is None:
                continue

            merge_lookup_collection(branch.levels, other_branch.levels)
            branch.bind |= other_branch.bind

        branches |= other_branches

    self |= other

