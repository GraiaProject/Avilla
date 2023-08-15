from __future__ import annotations

import contextlib

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol
from graia.amnesia.builtins.memcache import MemcacheService

from .service import RedService


class RedProtocol(BaseProtocol):
    service: RedService

    def __init__(self):
        self.service = RedService(self)

    @classmethod
    def __init_isolate__(cls):
        # isort: off

        # :: Message
        from .perform.message.deserialize import RedMessageDeserializePerform  # noqa: F401
        from .perform.message.serialize import RedMessageSerializePerform  # noqa: F401

        ## :: Action
        # from .perform.action.contact import RedContactActionPerform
        from .perform.action.friend import RedFriendActionPerform  # noqa: F401
        from .perform.action.group import RedGroupActionPerform  # noqa: F401

        # from .perform.action.group_member import RedGroupMemberActionPerform
        from .perform.action.message import RedMessageActionPerform  # noqa: F401

        ## :: Event
        from .perform.event.message import RedEventMessagePerform  # noqa: F401
        from .perform.event.lifespan import RedEventLifespanPerform  # noqa: F401

        ## :: Query
        from .perform.query import RedQueryPerform  # noqa: F401

        ## :: Resource Fetch
        from .perform.resource_fetch import RedResourceFetchPerform  # noqa: F401

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)
        with contextlib.suppress(ValueError):
            avilla.launch_manager.add_component(MemcacheService())
