from __future__ import annotations

from datetime import datetime

from satori.model import Channel, Event, Login, Member, MessageObject, Role, User


class OuterEvent(Event):
    id: int
    type: str
    platform: str
    self_id: str
    timestamp: datetime
    channel: Channel
    login: Login
    member: Member
    message: MessageObject
    operator: User
    role: Role
    user: User
