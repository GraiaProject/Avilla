from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from graia.amnesia.message import MessageChain
from graia.broadcast.entities.dispatcher import BaseDispatcher

from avilla.core.event import AvillaEvent
from avilla.core.message import Message

if TYPE_CHECKING:
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface

    from avilla.core.selectors import entity
    from avilla.core.selectors import message as message_selector


class MessageReceived(AvillaEvent):
    message: Message

    @property
    def ctx(self) -> entity:
        return self.message.sender

    def __init__(self, message: Message, current_self: entity, time: datetime | None = None) -> None:
        self.message = message
        self.self = current_self
        self.time = time or datetime.now()

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["MessageReceived"]):
            if interface.annotation is Message:
                return interface.event.message
            elif interface.annotation is MessageChain:
                return interface.event.message.content


class MessageEdited(AvillaEvent):
    message: Message
    operator: entity
    past: MessageChain
    current: MessageChain

    @property
    def ctx(self) -> entity:
        return self.operator

    def __init__(
        self,
        message: Message,
        operator: entity,
        past: MessageChain,
        current: MessageChain,
        current_self: entity,
        time: datetime | None = None,
    ) -> None:
        self.message = message
        self.operator = operator
        self.past = past
        self.current = current
        self.self = current_self
        self.time = time or datetime.now()

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["MessageEdited"]):
            pass  # TODO


class MessageRevoked(AvillaEvent):
    message: message_selector

    operator: entity

    @property
    def ctx(self) -> entity:
        return self.operator

    def __init__(
        self,
        message: message_selector,
        operator: entity,
        current_self: entity,
        time: datetime | None = None,
    ) -> None:
        self.message = message
        self.operator = operator
        self.self = current_self
        self.time = time or datetime.now()

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["MessageRevoked"]):
            pass  # TODO
