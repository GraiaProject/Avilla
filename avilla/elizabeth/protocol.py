from __future__ import annotations

import base64
from datetime import datetime
from typing import Any, TypedDict, cast

from graia.amnesia.message import __message_chain_class__
from graia.amnesia.message.element import Element, Text

from avilla.core.application import Avilla
from avilla.core.elements import Audio, Notice, NoticeAll, Picture
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.protocol import BaseProtocol
from avilla.core.trait.context import wrap_artifacts
from avilla.elizabeth.connection.config import U_Config
from avilla.elizabeth.service import ElizabethService

from ..core.context import Context
from ..core.event import AvillaEvent
from ..spec.qq.elements import FlashImage
from .account import ElizabethAccount
from .util import ElementParse, ElementParser, EventParse, EventParser


class MessageDeserializeResult(TypedDict):
    content: list[Element]
    source: str
    time: datetime
    reply: str | None


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

    with wrap_artifacts() as event_parsers:
        import avilla.elizabeth.event.message as _

    with wrap_artifacts() as message_parsers:
        import avilla.elizabeth.message_parse as _

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

    async def serialize_message(self, message: __message_chain_class__, context: Context | None = None):
        result = []
        for element in message.content:
            if isinstance(element, Text):
                result.append({"type": "Plain", "text": element.text})
            elif isinstance(element, Notice):
                result.append({"type": "At", "target": int(element.target.last_value)})
            elif isinstance(element, NoticeAll):
                result.append({"type": "AtAll"})
            elif isinstance(element, Picture):
                raw = await (context or Context.current).fetch(element.resource)
                result.append(
                    {
                        "type": "Image",
                        "base64": base64.b64encode(raw).decode("utf-8"),
                    }
                )
            elif isinstance(element, FlashImage):
                raw = await (context or Context.current).fetch(element.resource)
                result.append(
                    {
                        "type": "FlashImage",
                        "base64": base64.b64encode(raw).decode("utf-8"),
                    }
                )
            elif isinstance(element, Audio):
                raw = await (context or Context.current).fetch(element.resource)
                result.append(
                    {
                        "type": "Voice",
                        "base64": base64.b64encode(raw).decode("utf-8"),
                    }
                )
        return result

    async def deserialize_message(self, context: Context, message: list[dict]):
        serialized: list[Element] = []
        result: dict[str, Any] = {
            "content": serialized,
            "source": str(message[0]["id"]),
            "time": datetime.fromtimestamp(message[0]["time"]),
        }
        for raw_element in message[1:]:
            if "type" not in raw_element:
                raise KeyError(f'expected "type" exists for {raw_element}')
            element_type = raw_element["type"]
            if element_type == "Quote":
                result["reply"] = str(raw_element["id"])
                continue
            parser: ElementParser | None = self.message_parsers.get(ElementParse(element_type))
            if parser is None:
                raise NotImplementedError(f'expected element "{element_type}" implemented for {raw_element}')
            serialized.append(await parser(context, raw_element))
        return cast("MessageDeserializeResult", result)

    async def parse_event(self, account: ElizabethAccount, event: dict) -> tuple[AvillaEvent, Context]:
        if "type" not in event:
            raise KeyError(f'expected "type" exists for {event}')
        event_type = event["type"]
        parser: EventParser | None = self.event_parsers.get(EventParse(event_type))
        if parser is None:
            raise NotImplementedError(f'expected event "{event_type}" implemented for {event}')
        return await parser(self, account, event)
