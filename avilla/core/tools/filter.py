import copy
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar, Union

from graia.broadcast.entities.decorator import Decorator
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.entities.exectarget import ExecTarget
from graia.broadcast.entities.signatures import Force
from graia.broadcast.exceptions import ExecutionStop
from graia.broadcast.interfaces.decorator import DecoratorInterface
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from avilla.core.message import MessageChain
from avilla.core.relationship import Relationship
from avilla.core.selectors import entity, mainline

S = TypeVar("S")
L = TypeVar("L")

R = TypeVar("R")
P = TypeVar("P")


@dataclass
class OmegaReport:
    completed: bool
    filter: "Filter"
    result: List[Any]
    stop_at: Optional[Callable] = None


class Filter(Decorator, Generic[S, L]):
    pre = True

    alpha: ExecTarget
    omega: Callable[[OmegaReport], L]
    chains: Dict[str, List[Callable[..., Any]]]
    names: Dict[str, Callable[..., Any]]

    ignore_execution_stop: bool = False
    default_value: Optional[L] = None
    default_factory_value: Optional[Callable[[], Optional[L]]] = None
    selected_branch: str = "main"

    current_end_callback: Optional[Callable[[List[Callable[..., Any]]], Any]] = None
    _end_origin_branch: Optional[str] = None

    def __init__(
        self,
        alpha: Callable[..., S] = lambda: None,
        omega: Callable[[OmegaReport], L] = lambda x: x.result[-1],
        initial_chain: List[Callable[..., Any]] = None,
    ):
        self.alpha = ExecTarget(alpha)
        self.omega = omega
        self.chains = {"main": initial_chain or []}
        self.names = {}

    def as_param(self):
        self.pre = False
        self.ignore_execution_stop = True
        return self

    def select(self, branch: str):
        self.selected_branch = branch
        return self

    def use(self: "Filter[Any, L]", new_step: Callable[[L], R], branch: str = None) -> "Filter[L, R]":
        self.chains[branch or self.selected_branch].append(new_step)
        return self  # type: ignore

    def name(self, name: str):
        self.names[name] = self.chains[self.selected_branch][-1]
        return self

    def copy(self):
        return copy.copy(self)

    def as_boolean(self: "Filter[S, L]") -> "Filter[S, bool]":
        def wrapped_omega(report: OmegaReport) -> bool:
            return bool(self.omega(report))

        self.omega = wrapped_omega
        return self  # type: ignore

    def default(self, value: L) -> "Filter[S, L]":
        self.default_value = value
        return self

    def default_factory(self, factory: Callable[[], L]) -> "Filter[S, L]":
        self.default_factory_value = factory
        return self

    def ignore_exec_stop(self):
        self.ignore_execution_stop = True
        return self

    @classmethod
    def message_chain(cls: "Type[Filter]") -> "Filter[MessageChain, Any]":
        def message_chain_getter_alpha(message_chain: MessageChain):
            return message_chain

        return cls(message_chain_getter_alpha, lambda report: report.result[-1], [])

    @classmethod
    def rs(cls: "Type[Filter[Relationship, Any]]") -> "Filter[Relationship, Any]":
        def relationship_getter_alpha(relationship: Relationship):
            return relationship

        return cls(relationship_getter_alpha, lambda report: report.result[-1], [])

    @classmethod
    def rsctx(cls: "Type[Filter]") -> "Filter[entity, Any]":
        def contactable_getter_alpha(relationship: Relationship):
            return relationship.ctx

        return cls(contactable_getter_alpha, lambda report: report.result[-1], [])

    @classmethod
    def mainline(cls: "Type[Filter]") -> "Filter[mainline, Any]":
        def mainline_getter_alpha(relationship: Relationship):
            return relationship.mainline

        return cls(mainline_getter_alpha, lambda report: report.result[-1], [])

    @classmethod
    def event(cls: "Type[Filter]", *event_types: Type[Dispatchable]) -> "Filter[Any, Dispatchable]":
        def event_getter_alpha(dispatcher_interface: DispatcherInterface):
            if dispatcher_interface.event.__class__ not in event_types:
                raise ExecutionStop
            return dispatcher_interface.event

        return cls(event_getter_alpha, lambda report: report.result[-1], [])

    @classmethod
    def optional_event(
        cls: "Type[Filter]", *event_types: Type[Dispatchable]
    ) -> "Filter[Any, Optional[Dispatchable]]":
        def optional_event_getter_alpha(dispatcher_interface: DispatcherInterface):
            if (
                dispatcher_interface.event is not None
                and dispatcher_interface.event.__class__ not in event_types
            ):
                raise ExecutionStop
            return dispatcher_interface.event

        return cls(optional_event_getter_alpha, lambda report: report.result[-1], [])

    @classmethod
    def constant(cls, value: L) -> "Filter[Any, L]":
        return cls(lambda: value, lambda report: report.result[-1], [])

    def id(self: "Filter[Any, entity]", *values: str) -> "Filter[entity, Any]":
        def id_getter_alpha(ctx: entity):
            if ctx.last() not in values:
                raise ExecutionStop

        self.use(id_getter_alpha)
        return self

    def group(
        self: "Filter[Any, Union[entity, mainline]]", *values: str
    ) -> "Filter[Union[entity, mainline], Any]":
        def group_getter_alpha(rsctx_or_mainline: Union[entity, mainline]):
            return rsctx_or_mainline["group"] in values

        self.use(group_getter_alpha)
        return self

    def end(self):
        if self.current_end_callback is None or self._end_origin_branch is None:
            raise TypeError("this context disallow end grammer.")
        if not self.selected_branch.startswith("$:"):
            raise ValueError("invalid context")
        if self.selected_branch not in self.chains:
            raise ValueError("empty branch")
        self.current_end_callback(self.chains[self.selected_branch])
        del self.chains[self.selected_branch]
        self.current_end_callback = None
        self.selected_branch = self._end_origin_branch
        self._end_origin_branch = None
        return self

    def parallel(self):
        self._end_origin_branch = self.selected_branch
        self.selected_branch = "$:parallel"
        self.current_end_callback = self._parallel_end_callback
        self.chains["$:parallel"] = []
        return self

    def _parallel_end_callback(self, chain: List[Callable[..., Any]]):
        def gathered_wrapper(upper_result: L):
            for i in chain:
                i(upper_result)

        self.use(gathered_wrapper, self._end_origin_branch)

    async def target(self, decorator_interface: DecoratorInterface):
        alpha_result: S = await decorator_interface.dispatcher_interface.broadcast.Executor(
            self.alpha,
            decorator_interface.dispatcher_interface.dispatchers,  # cannot be original...
        )

        step = None
        result: List[Any] = [alpha_result]

        try:
            for step in self.chains[self.selected_branch]:
                result.append(step(result[-1]))
        except ExecutionStop:
            self.omega(OmegaReport(completed=False, filter=self, result=result, stop_at=step))
            if not self.ignore_execution_stop:
                raise
            return None
        else:
            omega_result = self.omega(OmegaReport(completed=True, filter=self, result=result, stop_at=step))
            if isinstance(omega_result, Force):
                return omega_result.target
            return (
                omega_result
                or self.default_value
                or (self.default_factory_value and self.default_factory_value())
                or None
            )
