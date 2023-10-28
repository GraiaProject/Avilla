from __future__ import annotations

from typing import Any, Callable

from avilla.core.metadata import Route
from graia.ryanvk.collector import BaseCollector
from graia.ryanvk.overload import FnOverload


class MetadataOverload(FnOverload):
    def collect_entity(
        self,
        collector: BaseCollector,
        scope: dict[Any, Any],
        entity: Any,
        params: dict[str, Route],
    ) -> None:
        record = (collector, entity)

        for param, route in params.items():
            ...
            collection: dict[Route, set] = scope.setdefault(param, {})
            collection.setdefault(route, set()).add(record)

    def get_entities(self, scope: dict[Any, Any], args: dict[str, Route]) -> set[tuple[BaseCollector, Callable]]:
        sets: list[set] = []

        for arg_name, route in args.items():
            if arg_name not in scope:
                raise NotImplementedError

            collection = scope[arg_name]

            if route not in collection:
                raise NotImplementedError

            sets.append(collection[route])

        return sets.pop().intersection(*sets)

    def merge_scopes(self, *scopes: dict[Any, Any]):
        # layout: {param_name: {route: set()}}
        result = {}

        for scope in scopes:
            for param_name, collection in scope.items():
                result_collection = result.setdefault(param_name, {})
                for route, entities in collection.items():
                    routes = result_collection.setdefault(route, set())
                    routes.update(entities)

        return result
