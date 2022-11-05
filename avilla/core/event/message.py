from __future__ import annotations

from dataclasses import dataclass
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


@dataclass
class MessageReceived(AvillaEvent):
    message: Message

    class Dispatcher(AvillaEvent.Dispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["MessageReceived"]):
            if interface.annotation is Message:
                return interface.event.message
            elif interface.annotation is MessageChain:
                return interface.event.message.content
            return await super().catch(interface)


@dataclass
class MessageEdited(AvillaEvent):
    message: Message
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
