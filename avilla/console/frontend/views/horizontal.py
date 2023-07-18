from textual.events import Resize
from textual.reactive import Reactive
from textual.widget import Widget

from avilla.console.frontend.components.chatroom import ChatRoom
from avilla.console.frontend.components.log import LogPanel

SHOW_LOG_BREAKPOINT = 120


class HorizontalView(Widget):
    DEFAULT_CSS = """
    HorizontalView {
        layout: horizontal;
        height: 100%;
        width: 100%;
        background: rgba(40, 44, 52, 1);
    }

    HorizontalView > * {
        height: 100%;
        width: 100%;
    }
    HorizontalView > .-w-50 {
        width: 50% !important;
    }
    
    HorizontalView > LogPanel {
        border-left: solid rgba(204, 204, 204, 0.7);
    }
    """

    can_show_log: Reactive[bool] = Reactive(False)
    show_log: Reactive[bool] = Reactive(True)

    def __init__(self):
        super().__init__()
        self.chatroom = ChatRoom()
        self.log_panel = LogPanel()

    def compose(self):
        yield self.chatroom
        yield self.log_panel

    def on_resize(self, event: Resize):
        self.responsive(event.size.width)

    def watch_can_show_log(self, can_show_log: bool):
        self._toggle_log_panel()

    def watch_show_log(self, show_log: bool):
        self._toggle_log_panel()

    def responsive(self, width: int) -> None:
        self.can_show_log = width > SHOW_LOG_BREAKPOINT  # type: ignore

    def action_toggle_log_panel(self):
        self.show_log = not self.show_log  # type: ignore

    def _toggle_log_panel(self):
        show = self.can_show_log and self.show_log
        self.log_panel.display = show
        self.chatroom.set_class(show, "-w-50")
        self.log_panel.set_class(show, "-w-50")
