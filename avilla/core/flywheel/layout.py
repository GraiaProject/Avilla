from __future__ import annotations

from collections import UserDict
from typing import Any, ItemsView, Iterator, KeysView, MutableMapping, MutableSequence, TypeVar, Mapping, ValuesView
from typing_extensions import TypeAlias

_K = TypeVar("_K")
_V = TypeVar("_V")


class DetailedArtifacts(UserDict, MutableMapping[_K, _V]):
    protected: bool = False


class ArtifactSlice(Mapping[_K, _V]):
    def __init__(self, origin: Mapping[_K, _V]) -> None:
        self._origin = origin
    
    def __getitem__(self, __key: _K) -> _V:
        return self._origin[__key]

    def __iter__(self) -> Iterator[_K]:
        return iter(self._origin)
    
    def __contains__(self, __key: object) -> bool:
        return __key in self._origin

    def keys(self) -> KeysView[_K]:
        return self._origin.keys()

    def values(self) -> ValuesView[_V]:
        return self._origin.values()

    def items(self) -> ItemsView[_K, _V]:
        return self._origin.items()

    def __len__(self) -> int:
        return len(self._origin)

LayoutContentT: TypeAlias = "ArtifactSlice[Any, Any] | DetailedArtifacts[Any, Any]"
LayoutT: TypeAlias = "MutableSequence[LayoutContentT]"
