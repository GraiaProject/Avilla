from __future__ import annotations

from contextvars import ContextVar
from typing import Any, ChainMap, MutableMapping

from .layout import DetailedArtifacts, LayoutT

GlobalArtifacts = DetailedArtifacts()
GlobalArtifacts.protected = True

GlobalLayout: LayoutT = [GlobalArtifacts]  # type: ignore

GlobalInstances = {}
Instances: ContextVar[ChainMap[type, Any]] = ContextVar("Instances", default=ChainMap(GlobalInstances))

AccessStack: ContextVar[MutableMapping[Any, list[int]]] = ContextVar("AccessStack")
Layout: ContextVar[LayoutT] = ContextVar("Layout")
