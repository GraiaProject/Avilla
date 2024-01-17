from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Generic, cast, overload
from typing_extensions import Concatenate, Self

from .._capability import CapabilityPerform
from ..collector import BaseCollector
from ..entity import BaseEntity
from .record import FnRecord
from ..perform import BasePerform
from ..typing import OutP, P, R, inRC

if TYPE_CHECKING:
    from .base import Fn
    from .overload import FnOverload


@dataclass
class FnImplementCollectCallback:
    implemented: dict[type[BasePerform], set[Fn]] = field(default_factory=dict)

    def __call__(self, _: type[BasePerform]):
        for owner, fns in self.implemented.items():
            if (
                issubclass(owner, CapabilityPerform)
                and not owner.__allow_incomplete__
                and not fns.issuperset(CapabilityPerform.__collector__.definations)
            ):
                raise NotImplementedError(
                    f"{owner} should implement all of {CapabilityPerform.__collector__.definations}"
                    f" but only {fns} are implemented"
                )


class FnImplementEntity(Generic[inRC, OutP], BaseEntity):
    fn: Fn[Callable[Concatenate[Any, OutP], Any], Any]
    impl: Callable[..., Any]

    def __init__(
        self,
        fn: Fn[Callable[Concatenate[Any, OutP], Any], Any],
        impl: inRC,
        *args: OutP.args,
        **kwargs: OutP.kwargs,
    ):
        self.fn = fn
        self.impl = impl

        self._collect_args = args
        self._collect_kwargs = kwargs

    def collect(self, collector: BaseCollector):
        super().collect(collector)

        record_signature = self.fn.compose_instance.signature()
        if record_signature not in collector.artifacts:
            record = collector.artifacts[record_signature] = cast(
                "FnRecord",
                {
                    "define": self.fn,
                    "overload_scopes": {},
                    "entities": {},
                },
            )
        else:
            record = collector.artifacts[record_signature]

        overload_scopes = record["overload_scopes"]
        twin = (collector, self.impl)

        triples: set[tuple[str, FnOverload, Any]] = set()

        for harvest_info in self.fn.compose_instance.collect(self.impl, *self._collect_args, **self._collect_kwargs):
            sign = harvest_info.overload.digest(harvest_info.value)
            scope = overload_scopes.setdefault(harvest_info.name, {})
            target_set = harvest_info.overload.collect(scope, sign)
            target_set[twin] = None
            triples.add((harvest_info.name, harvest_info.overload, sign))

        record["entities"][frozenset(triples)] = twin

        if self.fn.ownership is not None:
            for i in collector.collected_callbacks:
                if isinstance(i, FnImplementCollectCallback):
                    target = i
                    break
            else:
                target = FnImplementCollectCallback()
                collector.on_collected(target)

            if self.fn.ownership in target.implemented:
                fns = target.implemented[self.fn.ownership]
            else:
                fns = target.implemented[self.fn.ownership] = set()

            fns.add(self.fn)

        return self

    @overload
    def __get__(
        self: FnImplementEntity[Callable[Concatenate[Any, P], R], Any],
        instance: BasePerform,
        owner: type,
    ) -> FnImplementEntityAgent[Callable[P, R]]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type) -> Self:
        ...

    def __get__(self, instance: BasePerform | Any, owner: type):
        if not isinstance(instance, BasePerform):
            return self

        return FnImplementEntityAgent(instance, self)


class FnImplementEntityAgent(Generic[inRC]):
    perfrom: BasePerform
    entity: FnImplementEntity[inRC, ...]

    def __init__(self, perform: BasePerform, entity: FnImplementEntity) -> None:
        self.perform = perform
        self.entity = entity

    @property
    def __call__(self) -> inRC:
        def wrapper(*args, **kwargs):
            return self.entity.impl(self.perform, *args, **kwargs)

        return wrapper  # type: ignore

    @property
    def super(self) -> inRC:
        return self.entity.fn.callee
