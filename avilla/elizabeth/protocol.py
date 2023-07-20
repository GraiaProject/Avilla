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
        from .perform.action.activity import ElizabethActivityActionPerform
        from .perform.action.announcement import ElizabethAnnouncementActionPerform
        from .perform.action.contact import ElizabethContactActionPerform
        from .perform.action.friend import ElizabethFriendActionPerform
        from .perform.action.group import ElizabethGroupActionPerform
        from .perform.action.group_member import ElizabethGroupMemberActionPerform
        from .perform.action.message import ElizabethMessageActionPerform
        from .perform.action.request import ElizabethRequestActionPerform

        ## :: Event
        from .perform.event.activity import ElizabethEventActivityPerform
        from .perform.event.friend import ElizabethEventFriendPerform
        from .perform.event.group import ElizabethEventGroupPerform
        from .perform.event.group_member import ElizabethEventGroupMemberPerform
        from .perform.event.message import ElizabethEventMessagePerform
        from .perform.event.relationship import ElizabethEventRelationshipPerform
        from .perform.event.request import ElizabethEventRequestPerform

        # from .perform.event.lifespan import ElizabethEventLifespanPerform

        ## :: Query
        from .perform.query.bot import ElizabethBotQueryPerform
        from .perform.query.announcement import ElizabethAnnouncementQueryPerform
        from .perform.query.friend import ElizabethFriendQueryPerform
        from .perform.query.group import ElizabethGroupQueryPerform

        ## :: Resource Fetch
        from .perform.resource_fetch import ElizabethResourceFetchPerform

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)
