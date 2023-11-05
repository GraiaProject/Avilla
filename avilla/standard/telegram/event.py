from avilla.core.event import AvillaEvent


class ForumTopicEvent(AvillaEvent):
    ...


class ForumTopicClosed(ForumTopicEvent):
    ...


class ForumTopicCreated(ForumTopicEvent):
    ...


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
