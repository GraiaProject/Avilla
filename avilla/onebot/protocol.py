import json
from typing import Any, ClassVar, Final

from graia.broadcast import Dispatchable

from avilla.core.config import ConfigApplicant, ConfigFlushingMoment
from avilla.core.execution import Execution
from avilla.core.launch import LaunchComponent
from avilla.core.message import MessageChain
from avilla.core.platform import Platform
from avilla.core.protocol import BaseProtocol
from avilla.core.relationship import Relationship
from avilla.core.selectors import entity
from avilla.core.selectors import entity as entity_selector
from avilla.core.stream import Stream
from avilla.core.transformers import u8_string
from avilla.core.utilles.selector import Selector
from avilla.onebot.config import OnebotConnectionConfig
from avilla.onebot.event_parse import OnebotEventParser
from avilla.onebot.execution_ensure import OnebotExecutionHandler
from avilla.onebot.message_parse import OnebotMessageParser
from avilla.onebot.message_serialize import OnebotMessageSerializer
from avilla.onebot.service import OnebotService


class OnebotProtocol(BaseProtocol):
    platform: Final[Platform] = Platform(
        name="Onebot v11 for Avilla",
        protocol_provider_name="OneBot",
        implementation="avilla-onebot",
        supported_impl_version="$any",
        generation="v11",
    )

    execution_handler: Final[OnebotExecutionHandler] = OnebotExecutionHandler()
    message_parser: Final[OnebotMessageParser] = OnebotMessageParser()
    message_serializer: Final[OnebotMessageSerializer] = OnebotMessageSerializer()
    event_parser: Final[OnebotEventParser] = OnebotEventParser()
    service: OnebotService

    async def ensure_execution(self, execution: Execution):
        return await self.execution_handler.trig(self, execution)

    async def parse_message(self, data: list) -> MessageChain:
        result = []
        for raw_element in data:
            result.append(await self.message_parser.parse(self, raw_element))
        return MessageChain(result)

    async def parse_event(self, data: dict) -> Dispatchable:
        ...

    async def serialize_message(self, message: MessageChain) -> list:
        return await self.message_serializer.serialize(self, message)

    async def get_relationship(self, ctx: Selector, current_self: entity_selector) -> Relationship:
        if isinstance(ctx, entity):
            return Relationship(self, ctx, current_self)
        raise ValueError("cannot parse select")
