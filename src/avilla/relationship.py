from typing import Any, Generic, Union

from avilla.builtins.profile import GroupProfile, SelfProfile
from avilla.entity import Entity
from avilla.group import Group
from avilla.typing import T_Profile, T_Protocol


class Relationship(Generic[T_Profile, T_Protocol]):
    ctx: Union[Entity[T_Profile], Group]
    protocol: T_Protocol

    def __init__(self, ctx: Union[Entity[T_Profile], Group], protocol: T_Protocol) -> None:
        self.ctx = ctx
        self.protocol = protocol

    @property
    def current(self) -> Entity[SelfProfile]:
        return self.protocol.get_self()

    @property
    def profile(self) -> Union[T_Profile, GroupProfile]:
        return self.ctx.profile

    async def exec(self, *args, **kwargs) -> Any:
        assert 0 < len(args) <= 2
        if len(args) == 1:
            execution = args[0]
        else:
            target, execution = args
            return await self.protocol.ensure_execution(execution=execution.with_target(target))
        if kwargs.get("target"):
            target = kwargs["target"]
            return await self.protocol.ensure_execution(execution=execution.with_target(target))
        else:
            return await self.protocol.ensure_execution(execution=execution.with_target(self.ctx))
