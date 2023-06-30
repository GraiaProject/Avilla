from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, cast

from loguru import logger

from avilla.core.application import Avilla
from avilla.core.elements import Element
from avilla.core.protocol import BaseProtocol

from .descriptor.event import EventParserSign
from .descriptor.message.deserialize import MessageDeserializeSign
from .descriptor.message.serialize import MessageSerializeSign
from .service import OneBot11Service

if TYPE_CHECKING:
    from avilla.core.event import AvillaEvent
    from avilla.core.ryanvk.collector.protocol import ProtocolCollector
    from graia.amnesia.message import MessageChain

    from .account import OneBot11Account
    from .resource import OneBot11Resource


class OneBot11Protocol(BaseProtocol):
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

    def ensure(self, avilla: Avilla):
        avilla.launch_manager.add_component(OneBot11Service(self))

    async def parse_event(
        self,
        account: OneBot11Account,
        event_type: str,
        data: dict,
    ) -> AvillaEvent | None:
        sign = EventParserSign(event_type)
        if sign not in self.isolate.artifacts:
            logger.warning(f"Event {event_type} is not supported by {self.__class__.__name__}: {data}")
            return
        collector, entity = cast(
            """tuple[
                ProtocolCollector[OneBot11Protocol, OneBot11Account],
                Callable[[Any, dict], Awaitable[AvillaEvent]]
            ]""",
            self.isolate.artifacts[sign],
        )
        instance = collector.cls(self, account)
        return await entity(instance, data)

    async def serialize_message(self, account: OneBot11Account, message: MessageChain) -> list[dict]:
        result: list[dict] = []
        for element in message.content:
            element_type = type(element)
            sign = MessageSerializeSign(element_type)
            if sign not in self.isolate.artifacts:
                raise NotImplementedError(f"Element {element_type} is not supported by {self.__class__.__name__}")
            collector, entity = cast(
                """tuple[
                    ProtocolCollector[OneBot11Protocol, OneBot11Account],
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
                    ProtocolCollector[OneBot11Protocol, OneBot11Account],
                    Callable[[Any, dict], Awaitable[Element]]
                ]""",
                self.isolate.artifacts[sign],
            )
            instance = collector.cls(self, account)
            result.append(await entity(instance, raw_element))
        return MessageChain(result)

    async def fetch_resource(self, account: OneBot11Account, resource: OneBot11Resource) -> bytes:
        ...  # TODO
