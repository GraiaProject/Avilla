from __future__ import annotations

from contextvars import ContextVar
from typing import Any

processing_artifact_heap: ContextVar[dict[Any, Any]] = ContextVar("ryanvk#processing_artifact_heap")
