from dataclasses import dataclass
from typing import Optional, Union

from ..message.chain import MessageChain
from ..region import Region
from . import Operation, Result, TargetTypes


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
