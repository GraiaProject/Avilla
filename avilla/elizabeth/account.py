from __future__ import annotations

from typing import TYPE_CHECKING, Any

from avilla.core.account import AbstractAccount
from avilla.core.relationship import Relationship
from avilla.core.utilles.selector import Selector
from avilla.elizabeth.connection import ElizabethConnection
from avilla.elizabeth.connection.util import CallMethod

if TYPE_CHECKING:
    from .protocol import ElizabethProtocol


class ElizabethAccount(AbstractAccount):
    protocol: ElizabethProtocol

    async def get_relationship(self, target: Selector) -> Relationship:
        # TODO: 对象存在性检查
        if "land" not in target:
            target = Selector().mixin(f"land.{target.path}", target)
        if target.path in {"land.group", "land.friend"}:
            return Relationship(self.protocol, target, target, self.to_selector())
        elif target.path == "land.group.member":
            return Relationship(
                self.protocol,
                target,
                Selector().land(self.land.name).group(target.pattern["group"]),
                self.to_selector(),
            )
        else:
            raise NotImplementedError()

    @property
    def connection(self) -> ElizabethConnection:
        return self.protocol.service.get_connection(self.id)

    @property
    def available(self) -> bool:
        return self.connection.status.available

    async def call(
        self,
        command: str,
        method: CallMethod,
        params: dict,
        *,
        in_session: bool = True,
    ) -> Any:
        """发起一个调用

        Args:
            command (str): 调用命令
            method (CallMethod): 调用方法
            params (dict): 调用参数
            in_session (bool, optional): 是否在会话中. Defaults to True.

        Returns:
            Any: 调用结果
        """
        if in_session:
            await self.connection.status.wait_for_available()  # wait until session_key is present
            session_key = self.connection.status.session_key
            params["sessionKey"] = session_key
        return await self.connection.call(command, method, params)
