from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from typing_extensions import Concatenate, ParamSpec

if TYPE_CHECKING:
    from .collector import BaseCollector
    from .perform import BasePerform

P = ParamSpec("P")
R = TypeVar("R", covariant=True)

FnRecord = tuple[BaseCollector, Callable]


@dataclass(eq=True, frozen=True)
class FnImplement:
    owner: type[BasePerform]
    name: str


class Fn(Generic[P, R]):
    owner: type[BasePerform]
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
            collector.artifacts[signature] = (collector, entity)
            return entity

        return wrapper

    def get_artifact_record(
        self,
        collections: list[dict[Any, Any]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> tuple[BaseCollector, Callable[Concatenate[Any, P], Any]]:
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
