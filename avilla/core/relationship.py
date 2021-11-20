from contextlib import AsyncExitStack, asynccontextmanager
from datetime import timedelta
from typing import TYPE_CHECKING, Generic, List, Optional, Union

from avilla.core.builtins.profile import GroupProfile, SelfProfile
from avilla.core.contactable import Contactable
from avilla.core.context import ctx_rsexec_to, ctx_rsexec_period
from avilla.core.execution import Execution
from avilla.core.mainline import Mainline
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

    def to(self, target: Union[Contactable, Mainline]):
        @asynccontextmanager
        async def target_injector(rs: "Relationship", exec: Execution):
            if isinstance(target, Mainline):
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
    ctx: Contactable[T_Profile]
    protocol: "BaseProtocol"

    _middlewares: List[T_ExecMW]
    _self: Optional[Contactable[SelfProfile]]

    def __init__(
        self,
        ctx: Contactable[T_Profile],
        protocol: "BaseProtocol",
        middlewares: List[T_ExecMW] = None,
        current_self: Contactable[SelfProfile] = None,
    ) -> None:
        self.ctx = ctx
        self.protocol = protocol
        self._middlewares = middlewares or []
        self._self = current_self

    @property
    def current(self) -> Contactable[SelfProfile]:
        return self._self or self.protocol.get_self()

    @property
    def profile(self) -> Union[T_Profile, GroupProfile]:
        return self.ctx.profile

    @property
    def exec(self):
        return ExecutorWrapper(self)

    def has_ability(self, ability: str) -> bool:
        return self.protocol.has_ability(ability)
