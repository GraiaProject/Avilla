from __future__ import annotations

from typing import Any, Callable, TypedDict

from avilla.core.ryanvk.descriptor.query import QueryRecord, find_querier_steps
from avilla.core.selector import FollowsPredicater, _parse_follows
from graia.ryanvk import FnOverload, OverloadBehavior
from graia.ryanvk.collector import BaseCollector


class QueryCollectParams(TypedDict):
    target: str
    previous: str | None


class QueryCallArgs(TypedDict):
    pattern: str
    predicators: dict[str, FollowsPredicater]


class QueryOverload(FnOverload):
    identity: str = "query"

    def collect_entity(
        self,
        collector: BaseCollector,
        scope: dict[Any, Any],
        entity: Any,
        params: QueryCollectParams,
    ) -> None:
        record_tuple = (collector, entity)

        sign = QueryRecord(params["previous"], params["target"])
        scope.setdefault(sign, set()).add(record_tuple)

    def get_entities(
        self,
        scope: dict[QueryRecord, set[tuple[BaseCollector, Callable[..., Any]]]],
        args: QueryCallArgs,
    ):
        items = _parse_follows(args["pattern"], **args["predicators"])
        steps = find_querier_steps(scope, items)

        if steps is None:
            raise NotImplementedError

        ...


class QueryFnBehavior(OverloadBehavior):
    ...
