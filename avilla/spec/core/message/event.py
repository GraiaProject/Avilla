from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from graia.amnesia.message import MessageChain

from avilla.core.abstract.event import AvillaEvent
from avilla.core.abstract.message import ChatMessage, Message
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface


@dataclass
class MessageReceived(AvillaEvent):
    message: Message

    class Dispatcher(AvillaEvent.Dispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["MessageReceived"]):
            if interface.annotation is interface.event.message.__class__:
                return interface.event.message
            elif interface.annotation is MessageChain:
                if isinstance(interface.event.message, ChatMessage):
                    return interface.event.message.content
            return await super().catch(interface)


@dataclass
class MessageEdited(AvillaEvent):
    message: ChatMessage
    operator: Selector
    past: MessageChain
    current: MessageChain

    class Dispatcher(AvillaEvent.Dispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["MessageEdited"]):
            if interface.annotation is Message:
                return interface.event.message
            elif interface.annotation is MessageChain:
                return interface.event.current
            return await super().catch(interface)


@dataclass
class MessageRevoked(AvillaEvent):
    message: Selector
    operator: Selector

    class Dispatcher(AvillaEvent.Dispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["MessageRevoked"]):
            return await super().catch(interface)
