from dataclasses import dataclass

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


class ForumTopicEdited(ForumTopicEvent):
    ...


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


class VideoChatEvent(AvillaEvent):
    ...


class VideoChatEnded(VideoChatEvent):
    ...


class VideoChatParticipantsInvited(VideoChatEvent):
    ...


class VideoChatScheduled(VideoChatEvent):
    ...


class VideoChatStarted(VideoChatEvent):
    ...


class WriteAccessAllowed(AvillaEvent):
    ...
