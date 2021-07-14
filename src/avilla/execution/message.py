from dataclasses import dataclass
from . import Operation, Result, TargetTypes
from ..message.chain import MessageChain
from typing import Optional, Union
from ..region import Region


@dataclass
class MessageId:
    id: str  # 记得加上群组或者好友的ID.
    _id_region = Region("Message")


@dataclass
class MessageSend(Result[MessageId]):
    message: MessageChain
    reply: Optional[str] = None
    target = TargetTypes.CTX


@dataclass
class MessageRevoke(Operation):
    message_id: Union[MessageId, str]
    target = TargetTypes.MSG


@dataclass
class MessageEdit(Operation):
    message_id: Union[MessageId, str]
    to: MessageChain
    target = TargetTypes.MSG


@dataclass
class MessageFetch(Result[MessageChain]):
    message_id: Union[MessageId, str]
    target = TargetTypes.MSG


@dataclass
class MessageSendPrivate(MessageSend):
    pass
