from __future__ import annotations

from typing import ClassVar

from avilla.core import Avilla
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.protocol import BaseProtocol
from avilla.core.resource import PlatformResourceProvider
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
from avilla.elizabeth.service import ElizabethService


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

    platform_resource_providers: ClassVar[dict[Selector, type[PlatformResourceProvider]]] = {}
    protocol_metadata_providers: ClassVar[list[type[ProtocolMetadataSource]]] = []

    # 鉴于你 mah 乃至 mirai 还没支持频道, 这里就直接.
    completion_rules: ClassVar[dict[str, list[str]]] = {
        "group": ["land.group"],
        "friend": ["land.friend"],
        "member": ["land.group.member"],
        "contact": ["land.group.member"]  # Notice.target
        # TODO
    }

    service: ElizabethService

    def __init__(self, *config: U_Config):
        self.configs = config

    def ensure(self, avilla: Avilla):
        from .account import ElizabethAccount
        from .connection import CONFIG_MAP

        self.avilla = avilla
        self.service = ElizabethService(self)
        avilla.launch_manager.add_service(self.service)
        for config in self.configs:
            connection = CONFIG_MAP[config.__class__](self, config)
            self.service.connections.append(connection)
            avilla.launch_manager.add_launchable(connection)

            # TODO: hot registration of account
            avilla.add_account(ElizabethAccount(config.account, self))
