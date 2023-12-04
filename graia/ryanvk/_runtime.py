from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING, Any, MutableMapping

if TYPE_CHECKING:
    from .staff import Staff

targets_artifact_map: ContextVar[MutableMapping[Any, Any]]\
    = ContextVar("targets_artifact_map")  # fmt: off

upstream_staff: ContextVar[Staff]\
    = ContextVar("_StaffCtx")  # fmt: off
