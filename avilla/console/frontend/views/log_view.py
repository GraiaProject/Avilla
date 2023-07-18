from textual.widget import Widget

from avilla.console.frontend.components.log import LogPanel
from avilla.console.frontend.components.log.toolbar import Toolbar


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
