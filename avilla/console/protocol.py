from __future__ import annotations

from typing import TYPE_CHECKING
from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol
from avilla.console.frontend.info import Event
from loguru import logger
from .service import ConsoleService
from .staff import ConsoleStaff

if TYPE_CHECKING:
    from .account import ConsoleAccount


class ConsoleProtocol(BaseProtocol):
    service: ConsoleService
    name: str

    def __init__(self, name: str = "robot"):
        self.name = name

    @classmethod
    def __init_isolate__(cls):  # ruff: noqa: F401
        # isort: off

        # :: Message
        from .perform.message.deserialize import ConsoleMessageDeserializePerform
        from .perform.message.serialize import ConsoleMessageSerializePerform

        # :: Action
        from .perform.action.message import ConsoleMessageActionPerform
        from .perform.action.activity import ConsoleActivityActionPerform
        from .perform.action.profile import ConsoleProfileActionPerform

        # :: Event
        from .perform.event.message import ConsoleEventMessagePerform
        # from .perform.event.lifespan import OneBot11EventLifespanPerform


    def ensure(self, avilla: Avilla):
        self.avilla = avilla
        self.service = ConsoleService(self)
        avilla.launch_manager.add_component(self.service)

    async def parse_event(self, account: ConsoleAccount, event: Event):
        res = await ConsoleStaff(account).parse_event(event.type, event)
        if res is None:
            logger.warning(f"received unsupported event {event.type}: {event}")
            return
        logger.debug(f"{account.route['account']} received event {event.type}")
        self.post_event(res)
