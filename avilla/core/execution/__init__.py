from typing import Generic, TypeVar, TYPE_CHECKING, Optional

from avilla.core.message import MessageChain
from avilla.core.selectors import message as message_selector

from pydantic import BaseModel

if TYPE_CHECKING:
    from avilla.core.message import Message  # noqa: F401


class Execution(BaseModel):
    pass


R = TypeVar("R")


class Result(Generic[R]):
    pass


class MessageSend(Result[message_selector], Execution):
    message: MessageChain
    reply: Optional[str] = None

    def __init__(self, message: MessageChain, reply: Optional[str] = None):
        super().__init__(message=message, reply=reply)


class MessageRevoke(Execution):
    message: message_selector

    def __init__(self, message: message_selector):
        super().__init__(message=message)


class MessageEdit(Execution):
    message: message_selector
    to: MessageChain

    def __init__(self, message: message_selector, to: MessageChain):
        super().__init__(message=message, to=to)


class MessageFetch(Result["Message"], Execution):
    message: message_selector

    def __init__(self, message: message_selector):
        super().__init__(message=message)
