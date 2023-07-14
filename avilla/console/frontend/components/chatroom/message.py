from enum import Enum
from datetime import datetime

from textual.widget import Widget
from textual.widgets import Static
from rich.console import RenderableType

from ...utils import truncate
from ...info import User, MessageEvent


class Timer(Widget):
    DEFAULT_CSS = """
    Timer {
        layout: horizontal;
        height: 1;
        width: 100%;
        align: center middle;
    }
    Timer > Static {
        width: auto;
    }
    """

    def __init__(self, time: datetime):
        super().__init__()
        self.time = time

    def compose(self):
        yield Static(self.time.strftime("%H:%M"))


class Side(str, Enum):
    LEFT = "left"
    RIGHT = "right"


class Message(Widget):
    DEFAULT_CSS = """
    Message {
        layout: horizontal;
        height: auto;
        width: 100%;
        align-vertical: top;
        transition: offset 500ms out_cubic;
    }
    Message.left {
        align-horizontal: left;
    }
    Message.right {
        align-horizontal: right;
    }

    Message.left.-hidden {
        offset-x: -100%;
    }
    Message.right.-hidden {
        offset-x: 100%;
    }
    """

    def __init__(self, event: "MessageEvent"):
        self.event = event
        self.side: Side = Side.LEFT if event.user.id == event.self_id else Side.RIGHT
        super().__init__(
            classes="left -hidden" if self.side == Side.LEFT else "right -hidden"
        )

    def compose(self):
        if self.side == Side.LEFT:
            yield MessageAvatar(self.event.user)
            yield MessageInfo(self.event.user.nickname, self.event.message, self.side)
        else:
            yield MessageInfo(self.event.user.nickname, self.event.message, self.side)
            yield MessageAvatar(self.event.user)

    def on_show(self):
        self.remove_class("-hidden")


class MessageAvatar(Widget):
    DEFAULT_CSS = """
    MessageAvatar {
        layout: horizontal;
        content-align: center middle;
        text-align: center;
        height: 1;
        width: 3;
    }
    """

    def __init__(self, user: User):
        super().__init__()
        self.user = user

    def render(self):
        return self.user.avatar


class MessageInfo(Widget):
    DEFAULT_CSS = """
    $message-max-width: 65%;

    MessageInfo {
        layout: vertical;
        height: auto;
        width: 100%;
        max-width: $message-max-width;
    }
    MessageInfo > Static {
        height: 1;
        width: 100%;
        overflow: hidden;
        margin: 0 1;
    }
    MessageInfo.left > Static {
        text-align: left;
    }
    MessageInfo.right > Static {
        text-align: right;
    }
    """

    def __init__(self, nickname: str, renderable: RenderableType, side: Side):
        super().__init__(classes="left" if side == Side.LEFT else "right")
        self.nickname = truncate(nickname, 20)
        self.bubble = BubbleWrapper(renderable, side)

    def compose(self):
        yield Static(self.nickname)
        yield self.bubble


class BubbleWrapper(Widget):
    DEFAULT_CSS = """
    BubbleWrapper {
        height: auto;
        width: 100%;
        align-vertical: top;
    }
    BubbleWrapper.left {
        align-horizontal: left;
    }
    BubbleWrapper.right {
        align-horizontal: right;
    }
    """

    def __init__(self, renderable: RenderableType, side: Side):
        super().__init__(classes="left" if side == Side.LEFT else "right")
        self.renderable = renderable

    def compose(self):
        yield Bubble(self.renderable)


class Bubble(Widget):
    DEFAULT_CSS = """
    $bubble-border-type: round;
    $bubble-border-color: rgba(170, 170, 170, 0.7);
    $bubble-border: $bubble-border-type $bubble-border-color;

    Bubble {
        height: auto;
        width: auto;
        min-height: 1;
        max-width: 100%;
        padding: 0 1;
        border: $bubble-border;
    }
    """

    def __init__(self, renderable: RenderableType):
        super().__init__()
        self.renderable = renderable

    def render(self):
        return self.renderable
