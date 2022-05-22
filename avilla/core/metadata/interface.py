from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Type, TypeVar, overload

from avilla.core.metadata.model import Metadata
from avilla.core.metadata.source import MetadataSource

if TYPE_CHECKING:
    from typing_extensions import TypeGuard

class MetadataInterface:
    sources: list[MetadataSource]

    rules: dict[str, dict[Callable[[Any], TypeGuard[Any]], list[MetadataSource]]]
    # restriction, literal | typeguard, sources

    def __init__(self):
        self.sources = []
        self.rules = {
            "target": {}
        }

    def register(self, source: MetadataSource, **restructions: Callable[[Any], TypeGuard[Any]]) -> None:
        self.sources.append(source)
        for restriction, value in restructions.items():
            if restriction not in self.rules:
                self.rules[restriction] = {}
            if value not in self.rules[restriction]:
                self.rules[restriction][value] = []
            self.rules[restriction][value].append(source)

    if TYPE_CHECKING:
        T_target = TypeVar("T_target")
        T_metamodel = TypeVar("T_metamodel", bound=Metadata)

        @overload
        def get_source(self, target: T_target, metamodel: Type[T_metamodel]) -> MetadataSource[T_target, T_metamodel]: ...

        @overload
        def get_source(self, target: T_target, metamodel: Type[T_metamodel], *, **restrictions: Any) -> MetadataSource[T_target, T_metamodel]: ...

    def get_source(self, target: ..., metamodel: ..., *, **restrictions: Any):
        restrictions["target"] = target
        restrictions["metamodel"] = metamodel

        _set = None
        for restriction, value in restrictions.items():
            if restriction not in self.rules:
                raise ValueError(f"Unknown restriction: {restriction}")
            _i_set = [v for k, v in self.rules[restriction].items() if callable(k) and k(value)]
            if not _i_set:
                raise ValueError(f"No source found for {restriction} applying {value}")
            _i_set = set(_i_set[0]).intersection(*_i_set[1:])
            if _set is None:
                _set = _i_set
                continue
            _set.intersection_update(_i_set)
        assert _set is not None, "No source found for this target"
        if len(_set) > 1:
            raise ValueError("Multiple sources found, dichotomous conflict.")
        return list(_set)[0]
