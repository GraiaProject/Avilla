from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Generic, Protocol

from typing_extensions import Concatenate, ParamSpec, TypeVar

from graia.ryanvk.aio import queue_task

if TYPE_CHECKING:
    from .collector import BaseCollector  # noqa
    from .staff import Staff

P = ParamSpec("P")
P1 = ParamSpec("P1")
R = TypeVar("R", infer_variance=True)
T = TypeVar("T")
C = TypeVar("C", bound="BaseCollector")
CQ = TypeVar("CQ", bound="BaseCollector")


class SupportsCollect(Protocol[P, R]):
    def collect(self, collector: Any, *args: P.args, **kwargs: P.kwargs) -> R:  # type: ignore
        ...


class OutboundCompatible(Protocol[P, T, P1]):
    def get_artifact_record(
        self,
        collections: list[dict[Any, Any]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> RecordTwin[Any, Callable[Concatenate[Any, P], T]]:
        ...

    def get_outbound_callable(self, instance: Any, entity: Callable[Concatenate[Any, P], T]) -> Callable[P1, T]:
        ...


R1 = TypeVar("R1", covariant=True)
R2 = TypeVar("R2", covariant=True)


@dataclass(frozen=True, eq=True)
class Twin(Generic[R1, R2]):
    _0: R1
    _1: R2


class ClsIncluded(Protocol[T]):
    cls: type[T]


Cr = TypeVar("Cr", bound="BaseCollector", covariant=True)


class RecordTwin(Twin[Cr, R2]):
    def get_instance(self, staff: Staff):
        cls = self._0.cls
        if cls in staff.instances:
            return staff.instances[cls]

        instance = cls(staff)
        queue_task(staff.exit_stack.enter_async_context(instance.lifespan()))
        staff.instances[cls] = instance

        return instance

    def unwrap(self, staff: Staff):
        return self.get_instance(staff), self._1
