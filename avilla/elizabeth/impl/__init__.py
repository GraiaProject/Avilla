from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.traitof.context import prefix, raise_for_no_namespace, scope
from avilla.core.traitof.recorders import default_target, impl, pull, completes

raise_for_no_namespace()

# Relationship Complete

with scope("group"), prefix("group"):
    completes("member", "group.member")
