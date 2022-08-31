from __future__ import annotations

from typing import ClassVar

from avilla.core.application import Avilla
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.protocol import BaseProtocol
from avilla.core.trait.context import wrap_namespace
from avilla.core.utilles.selector import Selector
from avilla.elizabeth.connection.config import U_Config
from avilla.elizabeth.event_parser import ElizabethEventParser
from avilla.elizabeth.message_deserializer import ElizabethMessageDeserializer
from avilla.elizabeth.message_serializer import ElizabethMessageSerializer
from avilla.elizabeth.service import ElizabethService


class ElizabethProtocol(BaseProtocol):
    platform = Platform(
        Land(
            "qq",
            [{"name": "Tencent"}],
            humanized_name="QQ",
        ),
        Abstract(
            protocol="mirai-api-http",
            maintainers=[{"name": "royii"}],
            humanized_name="mirai-api-http protocol",
        ),
        Land(
            "elizabeth",
            [{"name": "GraiaProject"}],
            humanized_name="Elizabeth - mirai-api-http for avilla",
        ),
    )
    event_parser = ElizabethEventParser()
    message_serializer = ElizabethMessageSerializer()
    message_deserializer = ElizabethMessageDeserializer()
    """
    query_handlers: ClassVar[list[type[ProtocolAbstractQueryHandler]]] = [
        ElizabethGroupQuery,
        ElizabethRootQuery,
    ]
    """

    with wrap_namespace() as impl_namespace:
        import avilla.elizabeth.impl as _
        import avilla.elizabeth.impl.friend as _
        import avilla.elizabeth.impl.group as _

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
