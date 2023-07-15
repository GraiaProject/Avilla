from textual.widget import Widget

from ..components.log import LogPanel
from ..components.log.toolbar import Toolbar


class LogView(Widget):
    DEFAULT_CSS = """
    LogView {
        background: rgba(40, 44, 52, 1);
    }
    LogView > Toolbar {
        dock: top;
    }
    """

    def compose(self):
        yield Toolbar()
        yield LogPanel()
