from __future__ import annotations

from datetime import datetime

from satori.model import Channel, Event, Login, Member, Message, Role, User


class OuterEvent(Event):
    id: int
    type: str
    platform: str
    self_id: str
    timestamp: datetime
    channel: Channel
    login: Login
    member: Member
    message: Message
    operator: User
    role: Role
    user: User
