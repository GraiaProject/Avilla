from __future__ import annotations

from collections.abc import Iterable
from typing import Generic, Literal, TypeVar

from graia.amnesia.message import Element, MessageChain

from avilla.core.context import ctx_relationship
from avilla.core.elements import Text
from avilla.core.message import Message
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import message as message_selector
from avilla.core.selectors import request as request_selector


class Execution:
    located: bool = False
    locate_type: Literal["mainline", "ctx", "via", "current"] = "mainline"

    def locate_target(self, target: mainline_selector | entity_selector):
        self.located = True


R = TypeVar("R")


class Result(Generic[R]):
    pass


class MessageSend(Result[message_selector], Execution):
    target: entity_selector | mainline_selector
    message: MessageChain
    reply: message_selector | None = None

    def __init__(
        self,
        message: MessageChain | str | Iterable[str | Element],
        *,
        reply: Message | message_selector | str | None = None,
    ):
        if isinstance(message, str):
            message = MessageChain([Text(message)])
        elif not isinstance(message, MessageChain):
            result = MessageChain([])
            for element in message:
                result.append(element)
            message = result
        self.message = message
        if isinstance(reply, Message):
            reply = reply.to_selector()
        elif isinstance(reply, str):
            rs = ctx_relationship.get(None)
            if rs:
                reply = message_selector.mainline[rs.mainline]._[reply]
            else:
                reply = message_selector._[reply]
        self.reply = reply

    def locate_target(self, target: entity_selector | mainline_selector):
        self.located = True
        self.target = target


class MessageRevoke(Execution):
    message: message_selector

    def __init__(self, message: message_selector):
        self.message = message


class MessageEdit(Execution):
    message: message_selector
    to: MessageChain

    def __init__(self, message: message_selector, to: MessageChain):
        self.message = message
        self.to = to


class MessageFetch(Result[Message], Execution):
    message: message_selector

    def __init__(self, message: message_selector):
        self.message = message


class RequestAccept(Result[None], Execution):
    request: request_selector

    def __init__(self, request: request_selector):
        self.request = request


class RequestReject(Execution):
    request: request_selector

    def __init__(self, request: request_selector):
        self.request = request


class RelationshipDestroy(Execution):
    pass


class MemberRemove(Execution):
    member: entity_selector

    def __init__(self, member: entity_selector):
        self.member = member
