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
            return Relationship(self.protocol, target, target, self)
        elif target.path == "land.group.member":
            return Relationship(
                self.protocol,
                target,
                Selector().land(self.land.name).group(target.pattern["group"]),
                self,
            )
        else:
            raise NotImplementedError()

    @property
    def connection(self) -> ElizabethConnection:
        return self.protocol.service.get_connection(self.id)

    @property
    def available(self) -> bool:
        return self.connection.status.available

    async def call(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        params = params or {}
        method: CallMethod = params.pop("__method__")
        if params.pop("__use_session__", True):
            await self.connection.status.wait_for_available()  # wait until session_key is present
            session_key = self.connection.status.session_key
            params["sessionKey"] = session_key
        return await self.connection.call(endpoint, method, params)
