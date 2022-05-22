from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from avilla.core.resource import Resource, ResourceProvider

if TYPE_CHECKING:
    from typing_extensions import TypeGuard


class ResourceInterface:
    providers: list[ResourceProvider]

    rules: dict[str, dict[Callable[[Any], TypeGuard[Any]], list[ResourceProvider]]]
    # restriction, literal | typeguard, providers

    def __init__(self):
        self.providers = []
        self.rules = {
            "resource": {}
        }

    def register(self, provider: ResourceProvider, **restructions: Callable[[Any], TypeGuard[Any]]) -> None:
        self.providers.append(provider)
        for restriction, value in restructions.items():
            if restriction not in self.rules:
                self.rules[restriction] = {}
            if value not in self.rules[restriction]:
                self.rules[restriction][value] = []
            self.rules[restriction][value].append(provider)

    def get_provider(self, resource: Resource, /, **restrictions: Any) -> ResourceProvider:
        restrictions["resource"] = resource

        _set = None
        for restriction, value in restrictions.items():
            if restriction not in self.rules:
                raise ValueError(f"Unknown restriction: {restriction}")
            _i_set = [v for k, v in self.rules[restriction].items() if callable(k) and k(value)]
            if not _i_set:
                raise ValueError(f"No provider found for {restriction} applying {value}")
            _i_set = set(_i_set[0]).intersection(*_i_set[1:])
            if _set is None:
                _set = _i_set
                continue
            _set.intersection_update(_i_set)
        assert _set is not None, "No provider found for this target"
        if len(_set) > 1:
            raise ValueError("Multiple providers found, dichotomous conflict.")
        return list(_set)[0]
