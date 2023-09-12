from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, TypeVar

from typing_extensions import Concatenate, ParamSpec

from .aio import queue_task

if TYPE_CHECKING:
    from .collector import BaseCollector
    from .fn import Fn
    from .perform import BasePerform
    from .sign import FnImplement, FnRecord
    from .staff import Staff

T = TypeVar("T")
N = TypeVar("N", bound="BasePerform")
R = TypeVar("R", covariant=True)
P = ParamSpec("P")


class FnBehavior:
    def collect(
        self,
        collector: BaseCollector,
        fn: Fn[P, R, Any],  # type: ignore
        **overload_settings: Any,
    ):
        def wrapper(entity: Callable[Concatenate[Any, P], R]):
            artifact = collector.artifacts.setdefault(
                FnImplement(fn),
                {
                    "overload_enabled": fn.has_overload_capability,
                    "overload_scopes": {},
                    "record_tuple": None,
                },
            )
            if fn.has_overload_capability:
                for fn_overload, params in fn.overload_param_map.items():
                    scope = artifact["overload_scopes"].setdefault(fn_overload.identity, {})
                    fn_overload.collect_entity(
                        collector,
                        scope,
                        entity,
                        fn_overload.get_params_layout(params, overload_settings),
                    )
            else:
                artifact["record_tuple"] = (collector, entity)

            return entity

        return wrapper

    def harvest_record(self, staff: Staff, fn: Fn) -> FnRecord:
        return staff.artifact_map[FnImplement(fn)]

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

    def get_instance(self, staff: Staff, cls: type[N]) -> N:
        if cls not in staff.instances:
            instance = staff.instances[cls] = cls(staff)
            queue_task(staff.exit_stack.enter_async_context(instance.lifespan()))
        else:
            instance = staff.instances[cls]

        return instance

    def execute(
        self,
        staff: Staff,
        collector: BaseCollector,
        entity: Callable[Concatenate[Any, P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        # get instance
        instance = self.get_instance(staff, collector.cls)

        # execute
        return entity(instance, *args, **kwargs)


DEFAULT_BEHAVIOR = FnBehavior()
