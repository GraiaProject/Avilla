from __future__ import annotations

from contextvars import ContextVar
from typing import Any

processing_artifact_heap: ContextVar[dict[Any, Any]] = ContextVar("ryanvk#processing_artifact_heap")

GLOBAL_GALLERY = {}  # layout: {namespace: {identify: {...}}}, cover-mode.


def ref(namespace: str, identify: str | None = None) -> dict[Any, Any]:
    ns = GLOBAL_GALLERY.setdefault(namespace, {})
    scope = ns.setdefault(identify or "_", {})
    return scope