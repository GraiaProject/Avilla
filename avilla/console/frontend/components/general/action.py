from textual.events import Click
from textual.widgets import Static
from textual.binding import Binding
from textual.message import Message


class Action(Static, can_focus=True):
    DEFAULT_CSS = """
    $action-active-color: $accent;

    Action {
        text-align: center;
    }
    Action.left {
        dock: left;
    }
    Action.right {
        dock: right;
    }
    Action:focus, Action:hover {
        text-style: reverse;
    }
    """

    BINDINGS = [Binding("enter", "submit", "Perform action", priority=True)]

    class Pressed(Message):
        def __init__(self, target: "Action") -> None:
            super().__init__()
            self.target = target

        @property
        def action(self) -> "Action":
            return self.target

    def on_click(self, event: Click):
        event.stop()
        self.post_message(Action.Pressed(self))

    def action_submit(self):
        self.post_message(Action.Pressed(self))
