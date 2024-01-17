from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from contextvars import ContextVar
from typing import TYPE_CHECKING, Any, Callable, ContextManager, Final, Generic, Iterable, overload
from typing_extensions import Self, Concatenate

from .record import FnImplement
from ..operators import instances
from ..overloads import SingletonOverload
from ..typing import (
    P1,
    ExplictImplementShape,
    FnComposeCallReturnType,
    FnComposeCollectReturnType,
    ImplementForCollect,
    P,
    R,
    Twin,
    inTC,
)

if TYPE_CHECKING:
    from .base import Fn


class FnCompose(ABC):
    singleton = SingletonOverload().as_agent()

    fn: Fn

    def __init__(self, fn: Fn):
        self.fn = fn

    @property
    def collector(self):
        return self.fn.collector

    @abstractmethod
    def call(self) -> FnComposeCallReturnType[Any]:
        ...

    def collect(self, implement: Callable, **kwargs: Any) -> FnComposeCollectReturnType:
        ...

    def signature(self):
        return FnImplement(self.fn)

    @overload
    def harvest(self: ExplictImplementShape[inTC]) -> ContextManager[EntitiesHarvest[[inTC]]]:
        ...

    @overload
    def harvest(self: ImplementForCollect[P1]) -> ContextManager[EntitiesHarvest[P1]]:
        ...

    @contextmanager
    def harvest(self):
        harv = EntitiesHarvest()
        tok = EntitiesHarvest.mutation_endpoint.set(harv)

        try:
            yield harv
        finally:
            harv.finished = True
            EntitiesHarvest.mutation_endpoint.reset(tok)


class EntitiesHarvest(Generic[P1]):
    mutation_endpoint: Final[ContextVar[Self]] = ContextVar("EntitiesHarvest.mutation_endpoint")

    finished: bool = False
    _incompleted_result: dict[Twin, None] | None = None

    def commit(self, inbound: dict[Twin, None]) -> None:
        if self._incompleted_result is None:
            self._incompleted_result = inbound
            return

        self._incompleted_result = {k: inbound[k] if k in inbound else v for k, v in self._incompleted_result.items()}

    @property
    def ensured_result(self):
        if not self.finished or self._incompleted_result is None:
            raise LookupError("attempts to read result before its mutations all finished")

        return list(self._incompleted_result.keys())

    def ensure_twin(self, twin: Twin) -> Callable:
        collector, implement = twin
        instances_context = instances()

        if collector.cls not in instances_context:
            raise NotImplementedError("cannot find such perform in instances")

        instance = instances_context[collector.cls]

        def wrapper(*args, **kwargs):
            return implement(instance, *args, **kwargs)

        return wrapper  # type: ignore

    @property
    def first(self: EntitiesHarvest[Concatenate[Callable[P, R], ...]]) -> Callable[P, R]:
        result = self.ensured_result

        if not result:
            raise NotImplementedError("cannot lookup any implementation with given arguments")

        return self.ensure_twin(result[0])  # type: ignore

    def iter_result(self: EntitiesHarvest[Concatenate[Callable[P, R], ...]]) -> Iterable[Callable[P, R]]:
        return map(self.ensure_twin, self.ensured_result)  # type: ignore
