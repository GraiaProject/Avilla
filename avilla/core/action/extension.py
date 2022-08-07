from __future__ import annotations

from typing import TYPE_CHECKING, Any

from avilla.core.action import Action
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from avilla.core.relationship import RelationshipExecutor

class ActionExtension:
    ...