from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, cast

import aiohttp
from loguru import logger

from avilla.core.application import Avilla
from avilla.core.elements import Element
from avilla.core.protocol import BaseProtocol
from avilla.core.ryanvk.descriptor.message.deserialize import MessageDeserializeSign
from avilla.core.ryanvk.descriptor.message.serialize import MessageSerializeSign
from graia.amnesia.message import MessageChain

from .descriptor.event import EventParserSign
from .service import OneBot11Service

if TYPE_CHECKING:
    from avilla.core.event import AvillaEvent
    from avilla.core.ryanvk.collector.account import AccountCollector
    from .collector.connection import ConnectionCollector
    from .net.ws_client import OneBot11WsClientNetworking

    from .account import OneBot11Account
    from .resource import OneBot11Resource


class OneBot11Protocol(BaseProtocol):
    service: OneBot11Service

    def __init__(self):
        self.service = OneBot11Service(self)

    @classmethod
    def __init_isolate__(cls):  # ruff: noqa: F401
        # isort: off

        # :: Message
        from .perform.message.deserialize import OneBot11MessageDeserializePerform
        from .perform.message.serialize import OneBot11MessageSerializePerform

        # :: Action
        from .perform.action.message import OneBot11MessageActionPerform

        # :: Event
        from .perform.event.message import OneBot11EventMessagePerform
        from .perform.event.lifespan import OneBot11EventLifespanPerform

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)

    async def parse_event(
        self,
        connection: OneBot11WsClientNetworking,
        event_type: str,
        data: dict,
    ) -> AvillaEvent | None:
        sign = EventParserSign(event_type)
        if sign not in self.isolate.artifacts:
            logger.warning(f"Event {event_type} is not supported: {data}")
            return
        collector, entity = cast(
            """tuple[
                ConnectionCollector,
                Callable[[Any, dict], Awaitable[AvillaEvent | None]]
            ]""",
            self.isolate.artifacts[sign],
        )
        instance = collector.cls(self, connection)
        return await entity(instance, data)

    async def serialize_message(self, account: OneBot11Account, message: MessageChain) -> list[dict]:
        result: list[dict] = []
        for element in message.content:
            element_type = type(element)
            sign = MessageSerializeSign(element_type)
            if sign not in self.isolate.artifacts:
                raise NotImplementedError(f"Element {element_type} is not supported")
            collector, entity = cast(
                """tuple[
                    AccountCollector[OneBot11Protocol, OneBot11Account],
                    Callable[[Any, Element], Awaitable[dict]]
                ]""",
                self.isolate.artifacts[sign],
            )
            instance = collector.cls(self, account)
            result.append(await entity(instance, element))
        return result

    async def deserialize_message(self, account: OneBot11Account, raw_elements: list[dict]) -> MessageChain:
        result: list[Element] = []
        for raw_element in raw_elements:
            element_type = raw_element["type"]
            sign = MessageDeserializeSign(element_type)
            if sign not in self.isolate.artifacts:
                raise NotImplementedError(f"Element {element_type} is not supported by {self.__class__.__name__}")
            collector, entity = cast(
                """tuple[
                    AccountCollector[OneBot11Protocol, OneBot11Account],
                    Callable[[Any, dict], Awaitable[Element]]
                ]""",
                self.isolate.artifacts[sign],
            )
            instance = collector.cls(self, account)
            result.append(await entity(instance, raw_element))
        return MessageChain(result)

    async def fetch_resource(self, account: OneBot11Account, resource: OneBot11Resource) -> bytes:
        # TODO: convert into universal method
        async with aiohttp.ClientSession() as session:
            async with session.get(resource.url) as resp:
                return await resp.read()
