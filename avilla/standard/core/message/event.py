from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from avilla.core.event import AvillaEvent
from graia.amnesia.message import MessageChain
from graia.broadcast.entities.signatures import Force
from avilla.core.account import BaseAccount

if TYPE_CHECKING:
    from avilla.core.message import Message
    from avilla.core.selector import Selector
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface


@dataclass
class MessageReceived(AvillaEvent):
    message: Message

    class Dispatcher(AvillaEvent.Dispatcher):
        @classmethod
        async def catch(cls, interface: DispatcherInterface[MessageReceived]):
            if interface.annotation is interface.event.message.__class__:
                return interface.event.message
            if interface.annotation is MessageChain:
                return interface.event.message.content
            if interface.name == "sender":
                return interface.event.message.sender
            return await AvillaEvent.Dispatcher.catch(interface)


@dataclass
class MessageSent(AvillaEvent):
    message: Message
    account: BaseAccount

    class Dispatcher(AvillaEvent.Dispatcher):
        @classmethod
        async def catch(cls, interface: DispatcherInterface[MessageSent]):
            if interface.annotation is interface.event.message.__class__:
                return interface.event.message
            if interface.annotation is MessageChain:
                return interface.event.message.content
            if issubclass(interface.annotation, BaseAccount):
                return interface.event.account
            return await AvillaEvent.Dispatcher.catch(interface)


@dataclass
class MessageEdited(AvillaEvent):
    message: Message
    operator: Selector
    past: MessageChain
    current: MessageChain

    class Dispatcher(AvillaEvent.Dispatcher):
        @classmethod
        async def catch(cls, interface: DispatcherInterface[MessageEdited]):
            if interface.annotation is Message:
                return interface.event.message
            if interface.annotation is MessageChain:
                return interface.event.current
            if interface.name == "sender":
                return interface.event.message.sender
            if interface.name == "operator":
                return interface.event.operator
            return await AvillaEvent.Dispatcher.catch(interface)


@dataclass
class MessageRevoked(AvillaEvent):
    message: Selector
    operator: Selector
    sender: Selector | None = None

    class Dispatcher(AvillaEvent.Dispatcher):
        @classmethod
        async def catch(cls, interface: DispatcherInterface[MessageRevoked]):
            if interface.name == "message":
                return interface.event.message
            if interface.name == "operator":
                return interface.event.operator
            if interface.name == "sender":
                return Force(interface.event.sender)
            return await AvillaEvent.Dispatcher.catch(interface)
