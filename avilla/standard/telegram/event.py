from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from avilla.core import Selector
from avilla.core.event import AvillaEvent, RelationshipEvent, SceneDestroyed


@dataclass
class ForumTopicEdited(RelationshipEvent):
    name: str
    icon_custom_emoji_id: str | None = None


@dataclass
class ForumTopicReopened(SceneDestroyed): ...


@dataclass
class GeneralForumTopicHidden(RelationshipEvent): ...


@dataclass
class GeneralForumTopicUnhidden(RelationshipEvent): ...


@dataclass
class MessageAutoDeleteTimerChanged(AvillaEvent):
    message_auto_delete_time: int


@dataclass
class ProximityAlertTriggered(AvillaEvent):
    traveler: Selector
    watcher: Selector
    distance: int


@dataclass
class VideoChatEvent(AvillaEvent):
    target: Selector


@dataclass
class VideoChatEnded(VideoChatEvent):
    duration: int


@dataclass
class VideoChatParticipantsInvited(VideoChatEvent):
    users: list[Selector]


@dataclass
class VideoChatScheduled(VideoChatEvent):
    start_date: datetime


@dataclass
class VideoChatStarted(VideoChatEvent): ...
