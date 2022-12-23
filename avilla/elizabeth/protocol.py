from __future__ import annotations
import base64

from avilla.core.abstract.trait.context import wrap_artifacts
from avilla.core.application import Avilla
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.protocol import BaseProtocol

from ..spec.qq.elements import FlashImage
from ..core.context import Context
from avilla.elizabeth.connection.config import U_Config
#from avilla.elizabeth.event_parser import ElizabethEventParser
#from avilla.elizabeth.message_deserializer import ElizabethMessageDeserializer
#from avilla.elizabeth.message_serializer import ElizabethMessageSerializer
from avilla.elizabeth.service import ElizabethService

from graia.amnesia.message import MessageChain
from graia.amnesia.message.element import Text
from avilla.core.elements import Audio, Notice, NoticeAll, Picture


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

    with wrap_artifacts() as implementations:
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

    async def serialize_message(self, message: MessageChain):
        result = []
        for element in message.content:
            if isinstance(element, Text):
                result.append({"type": "Plain", "text": element.text})
            elif isinstance(element, Notice):
                result.append({"type": "At", "target": int(element.target.latest_value)})
            elif isinstance(element, NoticeAll):
                result.append({"type": "AtAll"})
            elif isinstance(element, Picture):
                raw = await Context.app_current.fetch(element.resource)
                result.append(
                    {
                        "type": "Image",
                        "base64": base64.b64encode(raw).decode("utf-8"),
                    }
                )
            elif isinstance(element, FlashImage):
                raw = await Context.app_current.fetch(element.resource)
                result.append(
                    {
                        "type": "FlashImage",
                        "base64": base64.b64encode(raw).decode("utf-8"),
                    }
                )
            elif isinstance(element, Audio):
                raw = await Context.app_current.fetch(element.resource)
                result.append(
                    {
                        "type": "Voice",
                        "base64": base64.b64encode(raw).decode("utf-8"),
                    }
                )
        return result