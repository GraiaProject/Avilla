from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from avilla.standard.core.application.event import AvillaLifecycleEvent

if TYPE_CHECKING:
    from avilla.core.account import BaseAccount


@dataclass
class AccountStatusChanged(AvillaLifecycleEvent):
    """指示当前账号 (Account) 状态发生改变的事件"""

    account: "BaseAccount"

    class Dispatcher(BaseDispatcher):
        @classmethod
        async def catch(cls, interface: DispatcherInterface[AccountStatusChanged]):
            from avilla.core.account import BaseAccount

            if issubclass(interface.annotation, BaseAccount):
                return interface.event.account

            return await AvillaLifecycleEvent.Dispatcher.catch(interface)


class AccountAvailable(AccountStatusChanged):
    """指示当前账号处于可用状态."""


class AccountRegistered(AccountAvailable):
    """指示当前账号 (Account) 被注册的事件"""


class AccountUnavailable(AccountStatusChanged):
    """指示当前账号处于不可用状态."""


class AccountUnregistered(AccountUnavailable):
    """指示当前账号 (Account) 被注销的事件"""
