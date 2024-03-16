from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .base import Fn
    from .overload import FnOverload


@dataclass(slots=True)
class FnRecord:
    spec: Fn
    scopes: dict[str, dict[Any, Any]] = field(default_factory=dict)
    entities: dict[frozenset[tuple[str, "FnOverload", Any]], Callable] = field(default_factory=dict)


@dataclass(slots=True, unsafe_hash=True)
class FnImplement:
    fn: Fn
