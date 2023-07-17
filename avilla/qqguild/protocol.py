from __future__ import annotations

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol

from .service import QQGuildService


class QQGuildProtocol(BaseProtocol):
    service: QQGuildService

    def __init__(self):
        self.service = QQGuildService(self)

    @classmethod
    def __init_isolate__(cls):  # ruff: noqa: F401
        ...
        # isort: off

        # :: Message
        # from .perform.message.deserialize import QQGuildMessageDeserializePerform
        # from .perform.message.serialize import QQGuildMessageSerializePerform

        ## :: Action
        # from .perform.action.contact import QQGuildContactActionPerform
        # from .perform.action.friend import QQGuildFriendActionPerform
        # from .perform.action.group import QQGuildGroupActionPerform
        # from .perform.action.group_member import QQGuildGroupMemberActionPerform
        from .perform.action.message import QQGuildMessageActionPerform

        ## :: Event
        from .perform.event.message import QQGuildEventMessagePerform

        # from .perform.event.lifespan import QQGuildEventLifespanPerform

        ## :: Query
        # from .perform.query.group import QQGuildGroupQueryPerform

        ## :: Resource Fetch
        # from .perform.resource_fetch import QQGuildResourceFetchPerform

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)
