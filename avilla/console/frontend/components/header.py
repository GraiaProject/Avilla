from textual.reactive import Reactive
from textual.widgets import Header as TextualHeader
from textual.widgets._header import HeaderClock, HeaderIcon, HeaderTitle


class _Icon(HeaderIcon):
    def render(self):
        return "Avilla"


class Header(TextualHeader):
    DEFAULT_CSS = """
    Header {
        background: rgba(90, 99, 108, 0.6);
    }
    Header > HeaderIcon {
        color: #22b14c;
    }
    Header > HeaderTitle {
        color: rgba(229, 192, 123, 1);
    }
    """

    def __init__(self):
        super().__init__(show_clock=True)

    def compose(self):
        yield _Icon()
        yield HeaderTitle()
        yield HeaderClock()
