from __future__ import annotations

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol

from .service import RedService


class RedProtocol(BaseProtocol):
    service: RedService

    def __init__(self):
        self.service = RedService(self)

    @classmethod
    def __init_isolate__(cls):  # ruff: noqa: F401
        # isort: off

        # :: Message
        from .perform.message.deserialize import RedMessageDeserializePerform
        from .perform.message.serialize import RedMessageSerializePerform

        ## :: Action
        # from .perform.action.contact import RedContactActionPerform
        # from .perform.action.friend import RedFriendActionPerform
        from .perform.action.group import RedGroupActionPerform

        # from .perform.action.group_member import RedGroupMemberActionPerform
        from .perform.action.message import RedMessageActionPerform

        ## :: Event
        from .perform.event.message import RedEventMessagePerform
        from .perform.event.lifespan import RedEventLifespanPerform

        ## :: Query
        from .perform.query import RedQueryPerform

        ## :: Resource Fetch
        from .perform.resource_fetch import RedResourceFetchPerform

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)
