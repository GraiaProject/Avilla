from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from graia.amnesia.message import MessageChain
from graia.broadcast.entities.dispatcher import BaseDispatcher

from avilla.core.event import AvillaEvent
from avilla.core.message import Message
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface

    from avilla.core.account import AbstractAccount


class MessageReceived(AvillaEvent):
    message: Message

    @property
    def ctx(self) -> Selector:
        return self.message.sender

    def __init__(self, message: Message, account: AbstractAccount, time: datetime | None = None) -> None:
        self.message = message
        super().__init__(account, time=time)

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["MessageReceived"]):
            if interface.annotation is Message:
                return interface.event.message
            elif interface.annotation is MessageChain:
                return interface.event.message.content


class MessageEdited(AvillaEvent):
    message: Message
    operator: Selector
    past: MessageChain
    current: MessageChain

    @property
    def ctx(self):
        return self.operator

    def __init__(
        self,
        message: Message,
        operator: Selector,
        past: MessageChain,
        current: MessageChain,
        account: AbstractAccount,
        time: datetime | None = None,
    ) -> None:
        self.message = message
        self.operator = operator
        self.past = past
        self.current = current
        super().__init__(account, time=time)

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["MessageEdited"]):
            if interface.annotation is Message:
                return interface.event.message
            elif interface.annotation is MessageChain:
                return interface.event.current


class MessageRevoked(AvillaEvent):
    message: Selector
    operator: Selector

    @property
    def ctx(self):
        return self.operator

    def __init__(
        self,
        message: Selector,
        operator: Selector,
        account: AbstractAccount,
        time: datetime | None = None,
    ) -> None:
        self.message = message
        self.operator = operator
        super().__init__(account, time=time)

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["MessageRevoked"]):
            ...
