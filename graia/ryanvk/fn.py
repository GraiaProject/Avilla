from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Generic

from typing_extensions import Concatenate, ParamSpec, TypeVar

from graia.ryanvk.override import OverridePerformEntity
from graia.ryanvk.typing import RecordTwin

if TYPE_CHECKING:
    from .capability import Capability
    from .collector import BaseCollector
    from .perform import BasePerform
    from .typing import SupportsCollect


P = ParamSpec("P")
R = TypeVar("R", covariant=True)

T = TypeVar("T")
P1 = ParamSpec("P1")
P2 = ParamSpec("P2")
R2 = TypeVar("R2", covariant=True)
A = TypeVar("A", infer_variance=True)
WrapperCallable = Callable[[A], A]

FnRecord = tuple["BaseCollector", Callable]


@dataclass(eq=True, frozen=True)
class FnImplement:
    owner: type[BasePerform | Capability]
    name: str


class Fn(Generic[P, R]):
    owner: type[BasePerform | Capability]
    name: str
    shape: Callable

    def __init__(self, shape: Callable[Concatenate[Any, P], R]):
        self.shape = shape

    def __set_name__(self, owner: type[BasePerform], name: str):
        self.owner = owner
        self.name = name

    def collect(
        self,
        collector: BaseCollector,
        signature: Any,
    ):
        def wrapper(entity: Callable[Concatenate[Any, P], R]):
            collector.artifacts[signature] = RecordTwin(collector, entity)
            return entity

        return wrapper

    def get_artifact_record(
        self,
        collections: list[dict[Any, Any]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> RecordTwin[BaseCollector, Callable[Concatenate[Any, P], Any]]:
        signature = FnImplement(self.owner, self.name)
        for collection in collections:
            result = collection.get(signature)
            if result is not None:
                return result

        raise NotImplementedError

    def get_outbound_callable(self, instance: Any, entity: Callable[Concatenate[Any, P], R]):
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return entity(instance, *args, **kwargs)

        return wrapper

    def override(
        self: SupportsCollect[P1, Callable[[Callable[Concatenate[Any, P2], R2]], Any]],  # pyright: ignore
        collector: BaseCollector,
        *args: P1.args,
        **kwargs: P1.kwargs,
    ):
        def wrapper(entity: Callable[Concatenate[Any, P2], R2]) -> OverridePerformEntity[P2, R2]:
            self.collect(collector, *args, **kwargs)(entity)
            return OverridePerformEntity(collector, self, entity)  # type: ignore

        return wrapper
