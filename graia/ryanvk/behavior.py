from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, TypeVar

from typing_extensions import Concatenate, ParamSpec

from .sign import FnImplement, FnRecord

if TYPE_CHECKING:
    from .collector import BaseCollector
    from .fn import Fn
    from .perform import BasePerform
    from .staff import Staff

T = TypeVar("T")
N = TypeVar("N", bound="BasePerform")
R = TypeVar("R", covariant=True)
P = ParamSpec("P")


class OverloadBehavior:
    def harvest_record(self, staff: Staff, fn: Fn) -> FnRecord:
        result = staff.artifact_map.get(FnImplement(fn))
        if result is None:
            raise NotImplementedError
        return result

    def harvest_overload(
        self, staff: Staff, fn: Fn[P, R], *args: P.args, **kwargs: P.kwargs
    ) -> tuple[BaseCollector, Callable[Concatenate[Any, P], R]]:
        artifact_record = self.harvest_record(staff, fn)

        if fn.has_overload_capability:
            bound_args = fn.shape_signature.bind(*args, **kwargs)
            bound_args.apply_defaults()
            collections = None

            for overload_item, required_args in fn.overload_param_map.items():
                scope = artifact_record["overload_scopes"][overload_item.identity]
                entities = overload_item.get_entities(scope, {i: bound_args.arguments[i] for i in required_args})
                collections = entities if collections is None else collections.intersection(entities)

            if not collections:
                raise NotImplementedError

            return collections.pop()  # type: ignore

        else:
            return artifact_record["record_tuple"]  # type: ignore



DEFAULT_BEHAVIOR = OverloadBehavior()
