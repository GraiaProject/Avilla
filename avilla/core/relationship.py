from contextlib import AsyncExitStack
from typing import TYPE_CHECKING, Any, Generic, List, Optional, Union

from avilla.core.builtins.profile import GroupProfile, SelfProfile
from avilla.core.contactable import Contactable
from avilla.core.execution import Execution
from avilla.core.typing import T_ExecMW, T_Profile

if TYPE_CHECKING:
    from avilla.core.protocol import BaseProtocol


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

    async def exec(self, execution: Execution, *user_middlewares: T_ExecMW) -> Any:
        middlewares = [*self._middlewares, *user_middlewares]

        async with AsyncExitStack() as exit_stack:
            for middleware in middlewares:
                await exit_stack.enter_async_context(middleware(self, execution))  # type: ignore
            return await self.protocol.ensure_execution(execution)

    def has_ability(self, ability: str) -> bool:
        return self.protocol.has_ability(ability)
