from __future__ import annotations

from contextvars import ContextVar
from typing import Any, ChainMap, MutableMapping, MutableSequence

from .layout import DetailedArtifacts

GlobalArtifacts = DetailedArtifacts()
GlobalArtifacts.protected = True

GlobalInstances = {}
Instances: ContextVar[ChainMap[type, Any]] = ContextVar("Instances", default=ChainMap(GlobalInstances))

AccessStack: ContextVar[MutableMapping[Any, list[int]]] = ContextVar("AccessStack")
Layout: ContextVar[MutableSequence[DetailedArtifacts[Any, Any]]] = ContextVar("Layout")
