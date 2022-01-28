from typing import TYPE_CHECKING, Generic, Iterable, Optional, TypeVar, Union

from avilla.core.elements import Text
from avilla.core.message import Element, MessageChain
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import message as message_selector
from avilla.core.selectors import request as request_selector

if TYPE_CHECKING:
    from avilla.core.message import Message


class Execution:
    pass


R = TypeVar("R")


class Result(Generic[R]):
    pass


class MessageSend(Result[message_selector], Execution):
    target: Union[entity_selector, mainline_selector]
    message: MessageChain
    reply: Optional[str] = None

    def __init__(self, message: Union[MessageChain, str, Iterable[Element]], reply: Optional[str] = None):
        if isinstance(message, str):
            message = MessageChain([Text(message)])
        elif isinstance(message, Iterable):
            message = MessageChain(list(message))
        self.message = message
        self.reply = reply

    def locate_target(self, target: Union[entity_selector, mainline_selector]):
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
    member: entity_selector

    def __init__(self, member: entity_selector):
        self.member = member
