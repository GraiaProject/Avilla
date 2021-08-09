from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel  # pylint: ignore

from avilla.entity import Entity
from avilla.group import Group

from ..message.chain import MessageChain
from . import Execution, Result, auto_update_forward_refs

EntityExecution = Execution[Union[Entity, Group, str]]


@dataclass
class MessageId:
    id: str  # 记得加上群组或者好友的ID(?).

    def __int__(self):
        return int(self.id)


MessageExecution = Execution[Union[MessageId, str]]


@auto_update_forward_refs
class MessageSend(Result[MessageId], EntityExecution):
    message: MessageChain
    reply: Optional[str] = None

    def __init__(self, message: MessageChain, reply: Optional[str] = None):
        super().__init__(message=message, reply=reply)


@auto_update_forward_refs
class MessageRevoke(MessageExecution):
    ...


@auto_update_forward_refs
class MessageEdit(MessageExecution):
    to: MessageChain

    def __init__(self, to: MessageChain):
        super().__init__(to=to)


@auto_update_forward_refs
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


@auto_update_forward_refs
class MessageSendPrivate(MessageSend):
    pass
