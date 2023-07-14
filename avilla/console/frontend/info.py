from dataclasses import dataclass, field
from datetime import datetime

from avilla.console.message import ConsoleMessage


@dataclass(frozen=True, eq=True)
class User:
    """用户"""

    id: str
    avatar: str = field(default="😃")
    nickname: str = field(default="User")


@dataclass(frozen=True, eq=True)
class Robot(User):
    """机器人"""

    avatar: str = field(default="🤖")
    nickname: str = field(default="Bot")


@dataclass
class Event:
    time: datetime
    self_id: str
    type: str
    user: User


@dataclass
class MessageEvent(Event):
    message: ConsoleMessage
