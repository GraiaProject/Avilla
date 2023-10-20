from __future__ import annotations

import sys
from contextlib import suppress
from typing import TYPE_CHECKING

from loguru import logger
from nonechat import Backend, Frontend
from nonechat.info import Event

from avilla.standard.core.account import (
    AccountAvailable,
    AccountRegistered,
    AccountUnavailable,
)

from ..core.account import AccountInfo
from .account import PLATFORM, ConsoleAccount
from .capability import ConsoleCapability

if TYPE_CHECKING:
    from .service import ConsoleService


class AvillaConsoleBackend(Backend):
    account: ConsoleAccount
    _service: ConsoleService

    def __init__(self, app: Frontend):
        super().__init__(app)
        self._stderr = sys.stdout
        self._logger_id: int | None = None
        self._should_restore_logger: bool = False

    def set_service(self, service: ConsoleService):
        self._service = service

    def on_console_load(self):
        logger.remove()
        self._should_restore_logger = True
        self.account = ConsoleAccount(self._service.protocol)
        self._logger_id = logger.add(self.frontend._fake_output, level=0, diagnose=False)
        self._service.protocol.avilla.accounts[self.account.route] = AccountInfo(
            self.account.route, self.account, self._service.protocol, PLATFORM
        )
        self._service.protocol.avilla.broadcast.postEvent(
            AccountRegistered(self._service.protocol.avilla, self.account)
        )

    def on_console_mount(self):
        self.account.status.enabled = True
        self._service.protocol.avilla.broadcast.postEvent(AccountAvailable(self._service.protocol.avilla, self.account))

    def on_console_unmount(self):
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
        del self._service.protocol.avilla.accounts[self.account.route]
        self._service.protocol.avilla.broadcast.postEvent(
            AccountUnavailable(self._service.protocol.avilla, self.account)
        )
        logger.success("Console exit.")
        logger.warning("Press Ctrl-C for Application exit")

    async def post_event(self, event: Event):
        with suppress(NotImplementedError):
            res = await self.account.staff.call_fn(ConsoleCapability.event_callback, event)
            self._service.protocol.post_event(res)
            return

        logger.warning(f"received unsupported event {event.type}: {event}")
