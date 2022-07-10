from __future__ import annotations

from typing import ClassVar

from avilla.core import Avilla
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.protocol import BaseProtocol
from avilla.core.resource import PlatformResourceProvider
from avilla.core.utilles.metadata_source import ProtocolMetadataSource
from avilla.core.utilles.selector import Selector
from avilla.elizabeth.action_executor import ElizabethGroupActionExecutor
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
    action_executors = [ElizabethGroupActionExecutor]

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

    def ensure(self, avilla: Avilla):
        from .connection.ws import WebsocketClientConnection, WebsocketClientInfo

        self.avilla = avilla
        self.service = ElizabethService(self)
        avilla.launch_manager.add_service(self.service)
        self.service.ensure_config(
            WebsocketClientConnection(
                self, WebsocketClientInfo(1779309090, "testafafv4fv34v34g3y45", "http://localhost:8080")
            )
        )
        for connection in self.service.connections:
            avilla.launch_manager.add_launchable(connection)

        """
        self.service.ensure_config(
            WebsocketClientConnection(self, WebsocketClientInfo(-1, "test", "http://localhost:8080"))
        )"""
