from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Generic

from typing_extensions import Concatenate

from ..entity import BaseEntity
from ..scoped import scoped_collect
from ..typing import CR, P
from .record import FnRecord

if TYPE_CHECKING:
    from .base import Fn
    from .overload import FnOverload, TCollectValue


@dataclass(slots=True)
class OverloadRecorder(Generic[CR]):
    target: FnRecord
    implement: CR
    operators: list[tuple[str, FnOverload, Any]] = field(default_factory=list)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.done()

    def done(self):
        for name, rule, value in self.operators:
            rule.lay(self.target, value, self.implement, name=name)

        self.target.entities[frozenset(self.operators)] = self.implement

    def use(self, target: FnOverload[Any, TCollectValue, Any], value: TCollectValue, *, name: str | None = None):
        self.operators.append((name or target.name, target, value))
        return self


class FnImplementEntity(Generic[CR], BaseEntity):
    targets: list[tuple[Fn, tuple[Any, ...], dict[str, Any]]]
    impl: CR

    def __init__(self, impl: CR):
        self.targets = []
        self.impl = impl

    def add_target(self, fn: Fn[Callable[Concatenate[Any, P], Any], Any], *args: P.args, **kwargs: P.kwargs):
        self.targets.append((fn, args, kwargs))

    def collect(self, collector: scoped_collect):
        super().collect(collector)

        for fn, args, kwargs in self.targets:
            record_signature = fn.desc.signature()
            if record_signature in collector.fn_implements:
                record = collector.fn_implements[record_signature]
            else:
                record = collector.fn_implements[record_signature] = FnRecord(fn)

            with OverloadRecorder(record, self.impl) as recorder:
                fn.desc.collect(recorder, *args, **kwargs)

        return self

    def _call(self, *args, **kwargs):
        return self.impl(*args, **kwargs)

    @property
    def __call__(self) -> CR:
        return self._call  # type: ignore

    @property
    def super(self) -> CR:
        return self.targets[0][0].__call__
