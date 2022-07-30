from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

if TYPE_CHECKING:
    from ..account import AbstractAccount
    from ..application import Avilla


class AvillaLifecycleEvent(Dispatchable):
    """指示有关应用 (Avilla) 的事件."""

    avilla: Avilla

    def __init__(self, avilla: Avilla):
        self.avilla = avilla

    class Dispatcher(BaseDispatcher):
        @classmethod
        async def catch(cls, interface: "DispatcherInterface[AvillaLifecycleEvent]"):
            from ..application import Avilla

            if interface.annotation is Avilla:
                return interface.event.avilla


class ApplicationClosing(AvillaLifecycleEvent):
    """指示 Avilla 正在关闭."""


class ApplicationClosed(AvillaLifecycleEvent):
    """指示 Avilla 已经关闭."""


class ApplicationPreparing(AvillaLifecycleEvent):
    """指示 Avilla 正在准备."""


class ApplicationReady(AvillaLifecycleEvent):
    """指示 Avilla 已准备完毕."""


@dataclass
class AccountStatusChanged(AvillaLifecycleEvent):
    """指示当前账号 (Account) 状态发生改变的事件"""

    account: "AbstractAccount"

    class Dispatcher(BaseDispatcher):
        @classmethod
        async def catch(cls, interface: "DispatcherInterface[AccountStatusChanged]"):
            from ..account import AbstractAccount

            if issubclass(interface.annotation, AbstractAccount):
                return interface.event.account


class AccountAvailable(AccountStatusChanged):
    """指示当前账号处于可用状态."""


class AccountUnavailable(AccountStatusChanged):
    """指示当前账号处于不可用状态."""
