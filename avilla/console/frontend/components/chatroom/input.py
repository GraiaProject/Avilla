from typing import TYPE_CHECKING, cast

from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import Input

if TYPE_CHECKING:
    from ...app import Frontend


class InputBox(Widget):
    DEFAULT_CSS = """
    $input-background: rgba(0, 0, 0, 0);
    $input-border-type: round;
    $input-border-color: rgba(170, 170, 170, 0.7);
    $input-border-active-color: $accent;
    $input-border: $input-border-type $input-border-color;
    $input-border-active: $input-border-type $input-border-active-color;

    InputBox {
        layout: horizontal;
        height: auto;
        width: 100%;
    }

    InputBox > Input {
        padding: 0 1;
        background: $input-background;
        border: $input-border !important;
    }
    InputBox > Input:focus {
        border: $input-border-active !important;
    }
    """

    BINDINGS = [
        Binding("escape", "blur", "Reset focus", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.input = Input(placeholder="Send Message")

    @property
    def app(self) -> "Frontend":
        return cast("Frontend", super().app)

    def compose(self):
        yield self.input

    async def on_input_submitted(self, event: Input.Submitted):
        event.stop()
        self.input.value = ""
        await self.app.action_post_message(event.value)

    def action_blur(self):
        self.input.blur()
