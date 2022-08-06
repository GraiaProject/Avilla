from __future__ import annotations

from typing import ClassVar

from avilla.core.application import Avilla
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.protocol import BaseProtocol
from avilla.core.querier import ProtocolAbstractQueryHandler
from avilla.core.resource import ProtocolResourceProvider
from avilla.core.utilles.metadata_source import ProtocolMetadataSource
from avilla.core.utilles.selector import Selector
from avilla.elizabeth.action_executor import (
    ElizabethFriendActionExecutor,
    ElizabethGroupActionExecutor,
    ElizabethGroupMemberActionExecutor,
)
from avilla.elizabeth.connection.config import U_Config
from avilla.elizabeth.event_parser import ElizabethEventParser
from avilla.elizabeth.message_deserializer import ElizabethMessageDeserializer
from avilla.elizabeth.message_serializer import ElizabethMessageSerializer
from avilla.elizabeth.query import ElizabethGroupQuery, ElizabethRootQuery
from avilla.elizabeth.service import ElizabethService

from .metadata_sources import (
    ElizabethGroupMetadataSource,
    ElizabethMemberMetadataSource,
)


class ElizabethProtocol(BaseProtocol):
    platform = Platform(
        Land(
            "elizabeth",
            [{"name": "GraiaProject"}],
            humanized_name="Elizabeth - mirai-api-http for avilla",
        ),
        Abstract(
            protocol="mirai-api-http",
            maintainers=[{"name": "royii"}],
            humanized_name="mirai-api-http protocol",
        ),
    )
    event_parser = ElizabethEventParser()
    message_serializer = ElizabethMessageSerializer()
    message_deserializer = ElizabethMessageDeserializer()
    action_executors = [
        ElizabethGroupActionExecutor,
        ElizabethFriendActionExecutor,
        ElizabethGroupMemberActionExecutor,
    ]

    resource_providers: ClassVar[dict[Selector, type[ProtocolResourceProvider]]] = {}
    metadata_providers: ClassVar[list[type[ProtocolMetadataSource]]] = [
        ElizabethGroupMetadataSource,
        ElizabethMemberMetadataSource,
    ]
    query_handlers: ClassVar[list[type[ProtocolAbstractQueryHandler]]] = [
        ElizabethGroupQuery,
        ElizabethRootQuery,
    ]

    # 鉴于你 mah 乃至 mirai 还没支持频道, 这里就直接.
    completion_rules = {
        "land.group": {
            "group": "land.group",
            "member": "land.group.member",
            "group.member": "land.group.member",
        },
        "land.friend": {"friend": "land.friend"},
        "land.contact": {"contact": "land.contact"},
        "land": {
            "contact": "land.contact",
        },
        "_": {
            "group": "land.group",
            "friend": "land.friend",
        }
        # TODO
    }

    service: ElizabethService

    def __init__(self, *config: U_Config):
        self.configs = config

    def ensure(self, avilla: Avilla):
        from .connection import CONFIG_MAP

        self.avilla = avilla
        self.service = ElizabethService(self)
        avilla.launch_manager.add_service(self.service)
        for config in self.configs:
            connection = CONFIG_MAP[config.__class__](self, config)
            self.service.connections.append(connection)
            avilla.launch_manager.add_launchable(connection)

            # LINK: see avilla.elizabeth.connection.{http|ws} for hot registration
