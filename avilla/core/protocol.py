from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, cast

from graia.amnesia.message import MessageChain

# from avilla.core.action.extension import ActionExtension
# from avilla.core.action.middleware import ActionMiddleware
from avilla.core._runtime import ctx_avilla, ctx_protocol
from avilla.core.account import AbstractAccount
from avilla.core.event import AvillaEvent
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.querier import ProtocolAbstractQueryHandler
from avilla.core.trait.context import Namespace
from avilla.core.utilles.event_parser import AbstractEventParser
from avilla.core.utilles.message_deserializer import MessageDeserializer
from avilla.core.utilles.message_serializer import MessageSerializer
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from avilla.core.application import Avilla


class BaseProtocol(metaclass=ABCMeta):
    avilla: Avilla
    platform: ClassVar[Platform]
    message_serializer: MessageSerializer
    message_deserializer: MessageDeserializer

    # completion_rules: ClassVar[dict[str, dict[str, str]]] = cast(dict, MappingProxyType({}))
    # action_middlewares: list[ActionMiddleware] = []

    event_parser: ClassVar[AbstractEventParser]
    # action_executors: ClassVar[list[type[ProtocolActionExecutor]]] = cast(list, ())
    # resource_providers: ClassVar[dict[str, type[ProtocolResourceProvider]]] = cast(dict, MappingProxyType({}))
    # query_handlers: ClassVar[list[type[ProtocolAbstractQueryHandler]]] = cast(list, ())
    # extension_impls: ClassVar[dict[type[ActionExtension], ActionExtensionImpl]] = cast(dict, MappingProxyType({}))

    impl_namespace: ClassVar[Namespace]

    def __init__(self):
        ...

    @property
    def land(self):
        return self.platform[Land]

    @property
    def abstract(self):
        return self.platform[Abstract]

    """
    @property
    def resource_labels(self) -> set[str]:
        return {pattern.path_without_land for pattern in self.resource_providers.keys()}
    """

    @abstractmethod
    def ensure(self, avilla: Avilla) -> Any:
        ...

    def get_accounts(self, selector: Selector | None = None) -> list[AbstractAccount]:
        return self.avilla.get_accounts(selector=selector, land=self.platform[Land])

    def get_account(self, selector: Selector) -> AbstractAccount | None:
        return self.avilla.get_account(selector=selector, land=self.platform[Land])

    async def parse_message(self, data: Any) -> MessageChain:
        return MessageChain(await self.message_deserializer.parse_sentence(self, data))

    async def serialize_message(self, message: MessageChain) -> Any:
        return await self.message_serializer.serialize_chain(self, message)

    def post_event(self, event: AvillaEvent):
        with ctx_avilla.use(self.avilla), ctx_protocol.use(self):
            self.avilla.broadcast.postEvent(event)
