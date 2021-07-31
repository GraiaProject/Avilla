from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Union

from pydantic.main import BaseModel
from datetime import datetime


from avilla.entity import Entity

from ..message.chain import MessageChain
from . import Execution, Operation, Result

EntityExecution = Execution[Union[Entity, str]]


@dataclass
class MessageId:
    id: str  # 记得加上群组或者好友的ID.


class MessageSend(BaseModel, Result[MessageId], EntityExecution):
    message: MessageChain  # type: ignore
    reply: Optional[str] = None


class MessageRevoke(BaseModel, Operation, EntityExecution):
    message_id: Union[MessageId, str]  # type: ignore


class MessageEdit(BaseModel, Operation, EntityExecution):
    message_id: Union[MessageId, str]  # type: ignore
    to: MessageChain  # type: ignore


class MessageFetch(BaseModel, Result["MessageFetchResult"], EntityExecution):
    message_id: Union[MessageId, str]  # type: ignore


class MessageFetchResult(BaseModel):
    time: datetime
    message_type: str
    message_id: str
    message: MessageChain

    class Config:
        extra = "ignore"


class MessageSendPrivate(MessageSend, EntityExecution):
    pass
