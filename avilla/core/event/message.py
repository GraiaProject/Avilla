from datetime import datetime

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from avilla.core.message import Message, MessageChain
from avilla.core.selectors import entity

from . import AvillaEvent


class MessageReceived(AvillaEvent):
    message: Message

    self: entity
    time: datetime

    def __init__(
        self,
        message: Message,
        self_: entity,
        time: datetime = None,
    ) -> None:
        self.message = message
        self.self = self_
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

    past: MessageChain
    current: MessageChain

    operator: entity

    self: entity
    time: datetime

    def __init__(
        self,
        message: Message,
        self_: entity,
        time: datetime = None,
    ) -> None:
        self.message = message
        self.self = self_
        self.time = time or datetime.now()

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


class MessageRevoked(AvillaEvent):
    message: Message

    operator: entity

    self: entity
    time: datetime

    def __init__(
        self,
        message: Message,
        self_: entity,
        time: datetime = None,
    ) -> None:
        self.message = message
        self.self = self_
        self.time = time or datetime.now()

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass
