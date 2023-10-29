from __future__ import annotations

from typing import Any, Callable

from graia.ryanvk.collector import BaseCollector


class FnOverload:
    @property
    def identity(self) -> str:
        return self.__class__.__name__

    def collect_entity(
        self,
        collector: BaseCollector,
        scope: dict[Any, Any],
        entity: Any,
        params: dict[str, Any],
    ) -> None:
        scope["_"] = {(collector, entity)}

    def get_entities(self, scope: dict[Any, Any], args: dict[str, Any]) -> set[tuple[BaseCollector, Callable]]:
        return scope["_"]

    def merge_scopes(self, *scopes: dict[Any, Any]) -> dict:
        return scopes[-1]

    def get_params_layout(self, params: list[str], args: dict[str, Any]) -> dict[str, Any]:
        return {param: args[param] for param in params}


class SimpleOverload(FnOverload):
    @property
    def identity(self) -> str:
        return str(id(self))

    def collect_entity(
        self,
        collector: BaseCollector,
        scope: dict[Any, Any],
        entity: Any,
        params: dict[str, Any],
    ) -> None:
        record = (collector, entity)

        for param_name, collect_info in params.items():
            collection = scope.setdefault(param_name, {})
            collection.setdefault(collect_info, set()).add(record)

    def get_entities(self, scope: dict[Any, Any], args: dict[str, Any]) -> set[tuple[BaseCollector, Callable]]:
        result_sets: list[set] = []

        for arg_name, arg_value in args.items():
            collection = scope[arg_name]
            if arg_value not in collection:
                raise NotImplementedError
            result_sets.append(collection[arg_value])

        return result_sets.pop().intersection(*result_sets)

    def merge_scopes(self, *scopes: dict[Any, Any]):
        # layout: {arg: {value: set}}

        result = {}

        for scope in scopes:
            for param_name, param_collection in scope.items():
                collection = result.setdefault(param_name, {})
                for value, entities in param_collection.items():
                    collection.setdefault(value, set()).update(entities)

        return result


class TypeOverload(FnOverload):
    @property
    def identity(self) -> str:
        return "type_overload:" + str(id(self))

    def collect_entity(
        self,
        collector: BaseCollector,
        scope: dict[Any, Any],
        entity: Any,
        params: dict[str, Any],
    ) -> None:
        record = (collector, entity)

        for param_name, collect_info in params.items():
            collection = scope.setdefault(param_name, {})
            collection.setdefault(collect_info, set()).add(record)

    def get_entities(self, scope: dict[Any, Any], args: dict[str, Any]) -> set[tuple[BaseCollector, Callable]]:
        result_sets: list[set] = []

        for arg_name, arg_value in args.items():
            collection = scope[arg_name]
            key = type(arg_value)
            if key not in collection:
                raise NotImplementedError
            result_sets.append(collection[key])

        return result_sets.pop().intersection(*result_sets)

    def merge_scopes(self, *scopes: dict[Any, Any]):
        # layout: {arg: {value: set}}

        result = {}

        for scope in scopes:
            for param_name, param_collection in scope.items():
                collection = result.setdefault(param_name, {})
                for value, entities in param_collection.items():
                    collection.setdefault(value, set()).update(entities)

        return result


class NoneOverload(FnOverload):
    default_factory: Callable[[str], Any] | None = None
    bypassing: FnOverload

    def __init__(self, bypassing: FnOverload, *, default_factory: Callable[[str], Any] | None = None) -> None:
        self.bypassing = bypassing
        self.default_factory = default_factory

    @property
    def identity(self) -> str:
        return "none_overload:" + str(id(self))

    def get_params_layout(self, params: list[str], args: dict[str, Any]) -> dict[str, Any]:
        if self.default_factory is not None:
            return {param: args.get(param) or self.default_factory(param) for param in params}
        return super().get_params_layout(params, args)

    def collect_entity(
        self,
        collector: BaseCollector,
        scope: dict[Any, Any],
        entity: Any,
        params: dict[str, Any],
    ) -> None:
        record = (collector, entity)
        if not scope:
            scope.update({"none": {}, "bypassing": {}})
        for param, collect_info in params.items():
            if collect_info is None:
                scope["none"].setdefault(param, set()).add(record)
            else:
                self.bypassing.collect_entity(
                    collector,
                    scope["bypassing"].setdefault(param, {}),
                    entity,
                    self.bypassing.get_params_layout([param], params),
                )

    def get_entities(
        self, scope: dict[Any, Any], args: dict[str, Any]
    ) -> set[tuple[BaseCollector, Callable[..., Any]]]:
        sets: list[set] = []
        none_collection = scope["none"]
        bypassing_collection = scope["bypassing"]

        for arg_name, arg_value in args.items():
            if arg_value is None:
                sets.append(none_collection[arg_name])
            else:
                sets.append(self.bypassing.get_entities(bypassing_collection[arg_name], {arg_name: arg_value}))

        return sets.pop().intersection(*sets)

class PredicateOverload(FnOverload):
    predicate: Callable[[str, Any], Any]

    def __init__(self, predicate: Callable[[str, Any], Any]) -> None:
        self.predicate = predicate

    @property
    def identity(self) -> str:
        return "predicate_overload:" + str(id(self))

    def collect_entity(
        self,
        collector: BaseCollector,
        scope: dict[Any, Any],
        entity: Any,
        params: dict[str, Any],
    ) -> None:
        record = (collector, entity)

        for param_name, collect_info in params.items():
            collection = scope.setdefault(param_name, {})
            collection.setdefault(collect_info, set()).add(record)

    def get_entities(self, scope: dict[Any, Any], args: dict[str, Any]) -> set[tuple[BaseCollector, Callable]]:
        result_sets: list[set] = []

        for arg_name, arg_value in args.items():
            collection = scope[arg_name]
            key = self.predicate(arg_name, arg_value)
            if key not in collection:
                raise NotImplementedError
            result_sets.append(collection[key])

        return result_sets.pop().intersection(*result_sets)

    def merge_scopes(self, *scopes: dict[Any, Any]):
        # layout: {arg: {value: set}}

        result = {}

        for scope in scopes:
            for param_name, param_collection in scope.items():
                collection = result.setdefault(param_name, {})
                for value, entities in param_collection.items():
                    collection.setdefault(value, set()).update(entities)

        return result
