import asyncio
import contextlib
import secrets
import sys
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional, TextIO, cast

from loguru import logger
from textual.app import App
from textual.binding import Binding
from textual.widgets import Input

from avilla.console.account import PLATFORM, ConsoleAccount
from avilla.console.element import Text
from avilla.console.message import ConsoleMessage
from avilla.core.account import AccountInfo
from avilla.core.ryanvk.staff import Staff
from avilla.standard.core.account import AccountAvailable, AccountUnavailable

from .components.footer import Footer
from .components.header import Header
from .info import Event, MessageEvent
from .log_redirect import FakeIO
from .router import RouterView
from .storage import Storage
from .views.horizontal import HorizontalView
from .views.log_view import LogView

if TYPE_CHECKING:
    from avilla.console.protocol import ConsoleProtocol


class Frontend(App):
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=False, priority=True),
        Binding("ctrl+d", "toggle_dark", "Toggle dark mode"),
        Binding("ctrl+s", "screenshot", "Save a screenshot"),
        Binding("ctrl+underscore", "focus_input", "Focus input", key_display="ctrl+/"),
    ]

    ROUTES = {"main": lambda: HorizontalView(), "log": lambda: LogView()}

    def __init__(self, protocol: "ConsoleProtocol"):
        super().__init__()
        self.protocol = protocol
        self.title = "Console"  # type: ignore
        self.sub_title = "Welcome to Avilla"  # type: ignore
        self.account = ConsoleAccount(protocol)
        self.storage = Storage()

        self._stderr = sys.stderr
        self._logger_id: Optional[int] = None
        self._should_restore_logger: bool = False
        self._fake_output = cast(TextIO, FakeIO(self.storage))
        self._redirect_stdout: Optional[contextlib.redirect_stdout[TextIO]] = None
        self._redirect_stderr: Optional[contextlib.redirect_stderr[TextIO]] = None

    def compose(self):
        yield Header()
        yield RouterView(self.ROUTES, "main")
        yield Footer()

    def on_load(self):
        logger.remove()
        self._should_restore_logger = True
        self._logger_id = logger.add(self._fake_output, level=0, diagnose=False)
        self.account.status.enabled = True

    def on_mount(self):
        self.protocol.avilla.accounts[self.account.route] = AccountInfo(
            self.account.route, self.account, self.protocol, PLATFORM
        )
        with contextlib.suppress(Exception):
            stdout = contextlib.redirect_stdout(self._fake_output)
            stdout.__enter__()
            self._redirect_stdout = stdout

        with contextlib.suppress(Exception):
            stderr = contextlib.redirect_stderr(self._fake_output)
            stderr.__enter__()
            self._redirect_stderr = stderr
        self.protocol.avilla.broadcast.postEvent(
            AccountAvailable(self.protocol.avilla, self.account)
        )

    def on_unmount(self):
        del self.protocol.avilla.accounts[self.account.route]
        if self._redirect_stderr is not None:
            self._redirect_stderr.__exit__(None, None, None)
            self._redirect_stderr = None
        if self._redirect_stdout is not None:
            self._redirect_stdout.__exit__(None, None, None)
            self._redirect_stdout = None

        if self._logger_id is not None:
            logger.remove(self._logger_id)
            self._logger_id = None
        if self._should_restore_logger:
            logger.add(
                self._stderr,
                backtrace=True,
                diagnose=True,
                colorize=True,
            )
            self._should_restore_logger = False
        self.account.status.enabled = False
        self.protocol.avilla.broadcast.postEvent(
            AccountUnavailable(self.protocol.avilla, self.account)
        )
        logger.success("Console exit.")
        logger.warning("Press Ctrl-C for Application exit")

    async def call(self, api: str, data: Dict[str, Any]):
        if api == "bell":
            await self.run_action("bell")
        elif api == "send_msg":
            msg_id = secrets.token_hex(16)
            with contextlib.suppress(Exception):
                self.storage.write_chat(
                    MessageEvent(
                        type="console.message",
                        time=datetime.now(),
                        self_id=data["info"].id,
                        msg_id=msg_id,
                        message=data["message"],
                        user=data["info"],
                    )
                )
                return msg_id

    def action_focus_input(self):
        with contextlib.suppress(Exception):
            self.query_one(Input).focus()

    async def action_post_message(self, message: str):
        msg = MessageEvent(
            type="console.message",
            time=datetime.now(),
            self_id=self.account.route["account"],
            msg_id=secrets.token_hex(16),
            message=ConsoleMessage([Text(message)]),
            user=self.storage.current_user,
        )
        self.storage.write_chat(msg)
        asyncio.create_task(self.post_event(self.account, msg))

    async def action_post_event(self, event: Event):
        asyncio.create_task(self.post_event(self.account, event))

    async def post_event(self, account: ConsoleAccount, event: Event):
        res = await Staff(account).parse_event(event.type, event)
        if res is None:
            logger.warning(f"received unsupported event {event.type}: {event}")
            return
        self.protocol.post_event(res)
