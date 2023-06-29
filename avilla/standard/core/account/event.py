from __future__ import annotations

from typing import TYPE_CHECKING

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from ..application.event import AvillaLifecycleEvent

from avilla.core._vendor.dataclasses import dataclass

if TYPE_CHECKING:
    from avilla.core.account import AbstractAccount

@dataclass
class AccountStatusChanged(AvillaLifecycleEvent):
    """指示当前账号 (Account) 状态发生改变的事件"""

    account: "AbstractAccount"

    class Dispatcher(BaseDispatcher):
        @classmethod
        async def catch(cls, interface: DispatcherInterface[AccountStatusChanged]):
            from avilla.core.account import AbstractAccount

            if issubclass(interface.annotation, AbstractAccount):
                return interface.event.account


class AccountAvailable(AccountStatusChanged):
    """指示当前账号处于可用状态."""


class AccountUnavailable(AccountStatusChanged):
    """指示当前账号处于不可用状态."""
