from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel  # pylint: ignore

from avilla.entity import Entity
from avilla.group import Group

from ..message.chain import MessageChain
from . import Execution, Result

EntityExecution = Execution[Union[Entity, Group, str]]


@dataclass
class MessageId:
    id: str  # 记得加上群组或者好友的ID(?).

    def __int__(self):
        return int(self.id)


MessageExecution = Execution[Union[MessageId, str]]


class MessageSend(Result[MessageId], EntityExecution):
    message: MessageChain
    reply: Optional[str] = None

    def __init__(self, message: MessageChain, reply: Optional[str] = None):
        super().__init__(message=message, reply=reply)


class MessageRevoke(MessageExecution):
    ...


class MessageEdit(MessageExecution):
    to: MessageChain

    def __init__(self, to: MessageChain):
        super().__init__(to=to)


class MessageFetch(Result["MessageFetchResult"], MessageExecution):
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
