from __future__ import annotations

from collections import UserDict
from typing import MutableMapping, TypeVar

_K = TypeVar("_K")
_V = TypeVar("_V")


class DetailedArtifacts(UserDict, MutableMapping[_K, _V]):
    protected: bool = False
