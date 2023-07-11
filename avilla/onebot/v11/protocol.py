from __future__ import annotations

from collections import ChainMap
from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar

import aiohttp
from loguru import logger
from typing_extensions import Concatenate

from avilla.core.application import Avilla
from avilla.core.elements import Element
from avilla.core.protocol import BaseProtocol
from avilla.core.ryanvk.descriptor.fetch import FetchImplement
from avilla.core.ryanvk.descriptor.message.deserialize import MessageDeserializeSign
from avilla.core.ryanvk.descriptor.message.serialize import MessageSerializeSign
from avilla.core.ryanvk.runner import run_fn, use_record
from graia.amnesia.message import MessageChain

from .descriptor.event import EventParserSign
from .service import OneBot11Service

if TYPE_CHECKING:
    from avilla.core.event import AvillaEvent
    from avilla.core.resource import Resource
    from avilla.core.ryanvk.collector.account import AccountCollector

    from .account import OneBot11Account
    from .collector.connection import ConnectionCollector
    from .net.ws_client import OneBot11WsClientNetworking
    from .resource import OneBot11Resource

T = TypeVar("T")


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

        # :: Resource Fetch
        from .perform.resource_fetch import OneBot11ResourceFetchPerform

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
        record: tuple[
            ConnectionCollector, Callable[[Any, dict], Awaitable[AvillaEvent | None]]
        ] = self.isolate.artifacts[sign]
        from devtools import debug

        async with use_record({"avilla": self.avilla, "protocol": self, "connection": connection}, record) as entity:
            return await entity(data)

    async def serialize_message(self, account: OneBot11Account, message: MessageChain) -> list[dict]:
        result: list[dict] = []
        for element in message.content:
            element_type = type(element)
            sign = MessageSerializeSign(element_type)
            if sign not in self.isolate.artifacts:
                raise NotImplementedError(f"Element {element_type} is not supported")
            async with use_record(
                {"avilla": self.avilla, "account": account, "protocol": self}, self.isolate.artifacts[sign]
            ) as entity:
                result.append(await entity(element))
        return result

    async def deserialize_message(self, account: OneBot11Account, raw_elements: list[dict]) -> MessageChain:
        result: list[Element] = []
        for raw_element in raw_elements:
            element_type = raw_element["type"]
            sign = MessageDeserializeSign(element_type)
            if sign not in self.isolate.artifacts:
                raise NotImplementedError(f"Element {element_type} is not supported by {self.__class__.__name__}")
            async with use_record(
                {"avilla": self.avilla, "account": account, "protocol": self}, self.isolate.artifacts[sign]
            ) as entity:
                result.append(await entity(raw_element))
        return MessageChain(result)

    async def fetch_resource(self, account: OneBot11Account, resource: Resource[T]) -> T:
        # TODO: convert into universal method
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(resource.url) as resp:
                return await resp.read()
        """
        record: tuple[Any, Callable[[Any, Resource[T]], Awaitable[T]]] = ChainMap(
            self.isolate.artifacts, self.avilla.isolate.artifacts
        )[FetchImplement(type(resource))]
        async with use_record(
            {"avilla": self.avilla, "account": account, "protocol": self},
            record,
        ) as entity:
            return await entity(resource)
