from typing import TYPE_CHECKING, cast

from textual.widget import Widget
from textual.widgets import Static

from ...router import RouteChange
from ..general.action import Action

if TYPE_CHECKING:
    from .history import ChatHistory
    from ...views.horizontal import HorizontalView


class Toolbar(Widget):
    DEFAULT_CSS = """
    $toolbar-border-type: round;
    $toolbar-border-color: rgba(170, 170, 170, 0.7);
    $toolbar-border: $toolbar-border-type $toolbar-border-color;

    Toolbar {
        layout: horizontal;
        height: 3;
        width: 100%;
        border: $toolbar-border;
        padding: 0 1;
    }

    Toolbar Static {
        width: 100%;
        content-align: center middle;
    }

    Toolbar Action {
        width: 3;
    }
    Toolbar Action.ml {
        margin-left: 4;
    }
    Toolbar Action.mr {
        margin-right: 4;
    }
    """

    def __init__(self):
        super().__init__()
        self.exit_button = Action("⛔", id="exit", classes="left")
        self.clear_button = Action("🗑️", id="clear", classes="left ml")
        self.center_title = Static("Chat", classes="center")
        self.settings_button = Action("⚙️", id="settings", classes="right mr")
        self.log_button = Action("📝", id="log", classes="right")

    def compose(self):
        yield self.exit_button
        yield self.clear_button

        yield self.center_title

        yield self.settings_button
        yield self.log_button

    async def on_action_pressed(self, event: Action.Pressed):
        event.stop()
        if event.action == self.exit_button:
            self.app.exit()
        elif event.action == self.clear_button:
            history = cast("ChatHistory", self.app.query_one("ChatHistory"))
            history.action_clear_history()
        elif event.action == self.settings_button:
            ...
        elif event.action == self.log_button:
            view = cast("HorizontalView", self.app.query_one("HorizontalView"))
            if view.can_show_log:
                view.action_toggle_log_panel()
            else:
                self.post_message(RouteChange("log"))  # noqa
