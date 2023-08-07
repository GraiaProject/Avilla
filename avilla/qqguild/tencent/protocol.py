from __future__ import annotations

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol

from .service import QQGuildService


class QQGuildProtocol(BaseProtocol):
    service: QQGuildService

    def __init__(self):
        self.service = QQGuildService(self)

    @classmethod
    def __init_isolate__(cls):
        ...
        # isort: off

        # :: Message
        from .perform.message.deserialize import QQGuildMessageDeserializePerform  # noqa: F401
        from .perform.message.serialize import QQGuildMessageSerializePerform  # noqa: F401

        ## :: Action
        from .perform.action.channel import QQGuildChannelActionPerform  # noqa: F401
        from .perform.action.guild import QQGuildGuildActionPerform  # noqa: F401
        from .perform.action.member import QQGuildMemberActionPerform  # noqa: F401
        from .perform.action.message import QQGuildMessageActionPerform  # noqa: F401
        from .perform.action.role import QQGuildRoleActionPerform  # noqa: F401

        ## :: Event
        from .perform.event.message import QQGuildEventMessagePerform  # noqa: F401
        from .perform.event.metadata import QQGuildEventMetadataPerform  # noqa: F401
        from .perform.event.relationship import QQGuildEventRelationshipPerform  # noqa: F401

        ## :: Query
        from .perform.query import QQGuildQueryPerform  # noqa: F401

        ## :: Resource Fetch
        from .perform.resource_fetch import QQGuildResourceFetchPerform  # noqa: F401

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)
