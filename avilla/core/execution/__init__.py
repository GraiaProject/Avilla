from typing import TYPE_CHECKING, Generic, Optional, TypeVar

from avilla.core.message import MessageChain
from avilla.core.selectors import entity, message as message_selector
from avilla.core.selectors import request as request_selector
from avilla.core.selectors import resource as resource_selector

if TYPE_CHECKING:
    from avilla.core.message import Message  # noqa: F401


class Execution:
    pass


R = TypeVar("R")


class Result(Generic[R]):
    pass


class MessageSend(Result[message_selector], Execution):
    message: MessageChain
    reply: Optional[str] = None

    def __init__(self, message: MessageChain, reply: Optional[str] = None):
        self.message = message
        self.reply = reply


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


class MessageFetch(Result["Message"], Execution):
    message: message_selector

    def __init__(self, message: message_selector):
        self.message = message


class RequestAccept(Result["None"], Execution):
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
    member: entity

    def __init__(self, member: entity):
        self.member = member
