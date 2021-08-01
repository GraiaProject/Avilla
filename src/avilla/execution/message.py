from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Union

from pydantic.main import BaseModel
from datetime import datetime


from avilla.entity import Entity
from avilla.group import Group

from ..message.chain import MessageChain
from . import Execution, Operation, Result

EntityExecution = Execution[Union[Entity, Group, str]]


@dataclass
class MessageId:
    id: str  # 记得加上群组或者好友的ID(?).


MessageExecution = Execution[Union[MessageId, str]]


class MessageSend(BaseModel, Result[MessageId], EntityExecution):
    message: MessageChain  # type: ignore
    reply: Optional[str] = None

    def __init__(self, message: MessageChain, reply: Optional[str] = None, target: Union[Entity, Group, str] = None):
        super().__init__(target=target, message=message, reply=reply)


class MessageRevoke(BaseModel, Operation, MessageExecution):
    def __init__(self, message_id: Union[MessageId, str]):
        super().__init__(target=message_id)


class MessageEdit(BaseModel, Operation, MessageExecution):
    to: MessageChain  # type: ignore

    def __init__(self, message_id: Union[MessageId, str], to: MessageChain):
        super().__init__(target=message_id, to=to)


class MessageFetch(BaseModel, Result["MessageFetchResult"], MessageExecution):
    def __init__(self, message_id: Union[MessageId, str]):
        super().__init__(target=message_id)


class MessageFetchResult(BaseModel):
    time: datetime
    message_type: str
    message_id: str
    message: MessageChain

    class Config:
        extra = "ignore"


class MessageSendPrivate(MessageSend):
    pass
