from __future__ import annotations

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol

from .service import ElizabethService


class ElizabethProtocol(BaseProtocol):
    service: ElizabethService

    def __init__(self):
        self.service = ElizabethService(self)

    @classmethod
    def __init_isolate__(cls):  # ruff: noqa: F401
        # isort: off

        # :: Message
        from .perform.message.deserialize import ElizabethMessageDeserializePerform
        from .perform.message.serialize import ElizabethMessageSerializePerform

        ## :: Action
        from .perform.action.contact import ElizabethContactActionPerform
        from .perform.action.friend import ElizabethFriendActionPerform
        from .perform.action.group import ElizabethGroupActionPerform
        from .perform.action.group_member import ElizabethGroupMemberActionPerform
        from .perform.action.message import ElizabethMessageActionPerform

        ## :: Event
        from .perform.event.message import ElizabethEventMessagePerform

        # from .perform.event.lifespan import ElizabethEventLifespanPerform

        ## :: Query
        from .perform.query.group import ElizabethGroupQueryPerform

        ## :: Resource Fetch
        from .perform.resource_fetch import ElizabethResourceFetchPerform

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)
