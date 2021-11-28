from contextlib import AsyncExitStack, asynccontextmanager
from datetime import timedelta
from typing import TYPE_CHECKING, Generic, List, Union

from avilla.core.context import ctx_rsexec_period, ctx_rsexec_to
from avilla.core.execution import Execution
from avilla.core.metadata import Metadata
from avilla.core.selectors import mainline, rsctx
from avilla.core.selectors import self as self_selector
from avilla.core.typing import T_ExecMW, T_Profile

if TYPE_CHECKING:
    from avilla.core.protocol import BaseProtocol


class ExecutorWrapper:
    relationship: "Relationship"
    execution: "Execution"
    middlewares: List[T_ExecMW]

    def __init__(self, relationship: "Relationship") -> None:
        self.relationship = relationship

    def __await__(self):
        exit_stack = AsyncExitStack()
        yield from exit_stack.__aenter__().__await__()
        try:
            for middleware in self.middlewares:
                yield from exit_stack.enter_async_context(
                    middleware(self.relationship, self.execution)  # type: ignore
                ).__await__()
            result = yield from self.relationship.protocol.ensure_execution(self.execution)
            return result
        finally:
            yield from exit_stack.__aexit__(None, None, None).__await__()

    def execute(self, execution: "Execution"):
        self.execution = execution
        return self

    __call__ = execute

    def to(self, target: Union[rsctx, mainline]):
        @asynccontextmanager
        async def target_injector(rs: "Relationship", exec: Execution):
            if isinstance(target, mainline):
                rs.protocol.check_mainline(target)
            with ctx_rsexec_to.use(target):
                yield

        self.middlewares.append(target_injector)  # type: ignore
        return self

    def period(self, period: timedelta):
        @asynccontextmanager
        async def period_injector(rs: "Relationship", exec: Execution):
            with ctx_rsexec_period.use(period):
                yield

        self.middlewares.append(period_injector)  # type: ignore
        return self

    def use(self, middleware: T_ExecMW):
        self.middlewares.append(middleware)
        return self


class Relationship(Generic[T_Profile]):
    ctx: rsctx
    mainline: mainline
    metadata: Metadata
    self: self_selector

    protocol: "BaseProtocol"

    _middlewares: List[T_ExecMW]

    def __init__(
        self,
        protocol: "BaseProtocol",
        ctx: rsctx,
        current_self: self_selector,
        middlewares: List[T_ExecMW] = None,
    ) -> None:
        self.ctx = ctx
        self.self = current_self
        self.protocol = protocol
        self._middlewares = middlewares or []

    @property
    def current(self) -> self_selector:
        return self.self or self.protocol.get_self()

    @property
    def exec(self):
        return ExecutorWrapper(self)

    def has_ability(self, ability: str) -> bool:
        return self.protocol.has_ability(ability)
