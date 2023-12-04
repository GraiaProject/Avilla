from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Generic, cast, overload

from typing_extensions import Concatenate, Self

from ryanvk.collector import BaseCollector
from ryanvk.entity import BaseEntity
from ryanvk.fn.record import FnRecord
from ryanvk.perform import BasePerform
from ryanvk.typing import P, R, inRC, specifiedCollectP

if TYPE_CHECKING:
    from ryanvk.fn.base import Fn
    from ryanvk.fn.overload import FnOverload


class FnImplementEntity(Generic[inRC, specifiedCollectP], BaseEntity):
    fn: Fn[Concatenate[Any, specifiedCollectP], Any]
    impl: Callable[..., Any]

    def __init__(
        self: FnImplementEntity[inRC, specifiedCollectP],
        fn: Fn[Concatenate[Any, specifiedCollectP], Any],
        impl: inRC,
        *args: specifiedCollectP.args,
        **kwargs: specifiedCollectP.kwargs,
    ):
        self.fn = fn
        self.impl = impl

        self._collect_args = args
        self._collect_kwargs = kwargs

    def collect(
        self: FnImplementEntity[inRC, specifiedCollectP],
        collector: BaseCollector,
    ):
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
            target_set.add(twin)
            triples.add((harvest_info.name, harvest_info.overload, sign))

        record["entities"][frozenset(triples)] = twin

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
    def staff(self):
        return self.perform.staff

    @property
    def __call__(self) -> inRC:
        def wrapper(*args, **kwargs):
            return self.entity.impl(self.perform, *args, **kwargs)

        return wrapper  # type: ignore

    @property
    def super(self) -> inRC:
        def wrapper(*args, **kwargs):
            return self.entity.fn.call(self.staff, *args, **kwargs)

        return wrapper  # type: ignore
