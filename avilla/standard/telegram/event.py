from dataclasses import dataclass
from datetime import datetime

from avilla.core import Selector
from avilla.core.event import AvillaEvent


@dataclass
class NewChatMember(AvillaEvent):
    target: Selector
    is_bot: bool
    username: str
    first_name: str


@dataclass
class ForumTopicEvent(AvillaEvent):
    target: Selector


@dataclass
class ForumTopicClosed(ForumTopicEvent):
    ...


@dataclass
class ForumTopicCreated(ForumTopicEvent):
    name: str
    icon_color: int
    icon_custom_emoji_id: str | None = None


@dataclass
class ForumTopicEdited(ForumTopicEvent):
    name: str
    icon_custom_emoji_id: str | None = None


class ForumTopicReopened(ForumTopicEvent):
    ...


class GeneralForumTopicHidden(ForumTopicEvent):
    ...


class GeneralForumTopicUnhidden(ForumTopicEvent):
    ...


class MessageAutoDeleteTimerChanged(AvillaEvent):
    ...


class SuccessfulPayment(AvillaEvent):
    ...


class ProximityAlertTriggered(AvillaEvent):
    ...


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


class VideoChatStarted(VideoChatEvent):
    ...


class WriteAccessAllowed(AvillaEvent):
    ...
