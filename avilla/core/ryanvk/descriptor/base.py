from __future__ import annotations

from typing import TYPE_CHECKING, Callable, TypeVar

from typing_extensions import Concatenate, ParamSpec

from ..common.fn import BaseFn, FnImplement

if TYPE_CHECKING:
    from ...context import Context
    from ..collector.context import ContextBasedPerformTemplate, ContextCollector
    from ..common.capability import Capability


P = ParamSpec("P")
R = TypeVar("R", covariant=True)
R1 = TypeVar("R1", covariant=True)
C = TypeVar("C", bound="Capability")
H = TypeVar("H", bound="ContextBasedPerformTemplate")


class Fn(BaseFn["ContextCollector", P, R]):
    def __init__(self, template: Callable[Concatenate[C, P], R]) -> None:
        self.template = template  # type: ignore

    def collect(self, collector: ContextCollector):
        def receive(entity: Callable[Concatenate[H, P], R]):
            collector.artifacts[FnImplement(self.capability, self.name)] = (collector, entity)
            return entity

        return receive

    def get_collect_signature(self):
        return FnImplement(self.capability, self.name)

    def get_artifact_record(
        self, runner: Context, *args: P.args, **kwargs: P.kwargs
    ) -> tuple[ContextCollector, Callable[Concatenate[ContextBasedPerformTemplate, P], R]]:
        return runner.artifacts[FnImplement(self.capability, self.name)]

    def execute(self, runner: Context, *args: P.args, **kwargs: P.kwargs) -> R:
        collector, entity = self.get_artifact_record(runner, *args, **kwargs)
        instance = collector.cls(runner)
        return entity(instance, *args, **kwargs)
