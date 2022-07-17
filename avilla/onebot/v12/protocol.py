from __future__ import annotations

from typing import ClassVar

from avilla.core import Avilla
from avilla.core.platform import Abstract, Land, Platform, Version
from avilla.core.protocol import BaseProtocol
from avilla.core.resource import PlatformResourceProvider
from avilla.core.utilles.metadata_source import ProtocolMetadataSource
from avilla.core.utilles.selector import Selector

from .event_parser import OneBot12EventParser
from .message_deserializer import OneBot12MessageDeserializer
from .message_serializer import OneBot12MessageSerializer
from .service import OneBot12Service


class OneBot12Protocol(BaseProtocol):
    platform = Platform(
        Land(
            name="onebot",
            maintainers=[{"name": "GraiaProject"}],
            humanized_name="OneBot",
        ),
        Abstract(
            protocol="onebot",
            maintainers=[{"name": "howmanybots"}],
            humanized_name="OneBot",
        ),
        Version(
            {
                "onebot_spec": "v12",
            }
        ),
    )
    event_parser = OneBot12EventParser()
    message_serializer = OneBot12MessageSerializer()
    message_deserializer = OneBot12MessageDeserializer()
    action_executors = [
        OneBot12GroupActionExecutor,
        OneBot12FriendActionExecutor,
        OneBot12GroupMemberActionExecutor,
    ]

    platform_resource_providers: ClassVar[dict[Selector, type[PlatformResourceProvider]]] = {}
    protocol_metadata_providers: ClassVar[list[type[ProtocolMetadataSource]]] = []

    completion_rules: ClassVar[dict[str, list[str]]] = {
        "group": ["land.group"],
        "friend": ["land.friend"],
        "member": ["land.group.member", "land.guild.channel.member"],  # 这样可以吗？
        "contact": ["land.group.member"]  # Notice.target
        # TODO
    }

    service: OneBot12Service

    def ensure(self, avilla: Avilla):
        pass
