from datetime import datetime

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from avilla.core.message import Message, MessageChain
from avilla.core.selectors import entity
from avilla.core.utilles.selector import Selector

from . import AvillaEvent


class MessageReceived(AvillaEvent):
    message: Message

    @property
    def ctx(self) -> Selector:
        return self.message.sender

    def __init__(
        self,
        message: Message,
        current_self: entity,
        time: datetime = None,
    ) -> None:
        self.message = message
        self.self = current_self
        self.time = time or datetime.now()

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: "DispatcherInterface[MessageReceived]"):
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
    def ctx(self) -> Selector:
        return self.operator

    def __init__(
        self,
        message: Message,
        operator: entity,
        past: MessageChain,
        current: MessageChain,
        current_self: entity,
        time: datetime = None,
    ) -> None:
        self.message = message
        self.operator = operator
        self.past = past
        self.current = current
        self.self = current_self
        self.time = time or datetime.now()

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


class MessageRevoked(AvillaEvent):
    message: Message

    operator: entity

    @property
    def ctx(self) -> Selector:
        return self.operator

    def __init__(
        self,
        message: Message,
        operator: entity,
        current_self: entity,
        time: datetime = None,
    ) -> None:
        self.message = message
        self.operator = operator
        self.self = current_self
        self.time = time or datetime.now()

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass
