from __future__ import annotations

from abc import ABCMeta, abstractmethod
from contextlib import ExitStack
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, ClassVar, cast

from graia.amnesia.message import MessageChain

from avilla.core.account import AbstractAccount
from avilla.core.action.extension import ActionExtension
from avilla.core.action.middleware import ActionMiddleware
from avilla.core.context import ctx_avilla, ctx_protocol
from avilla.core.event import AvillaEvent
from avilla.core.metadata.source import MetadataSource
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.querier import ProtocolAbstractQueryHandler
from avilla.core.resource import ProtocolResourceProvider, ResourceProvider
from avilla.core.typing import ActionExtensionImpl
from avilla.core.utilles.action_executor import ProtocolActionExecutor
from avilla.core.utilles.event_parser import AbstractEventParser
from avilla.core.utilles.message_deserializer import MessageDeserializer
from avilla.core.utilles.message_serializer import MessageSerializer
from avilla.core.utilles.metadata_source import ProtocolMetadataSource
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from avilla.core.application import Avilla


class BaseProtocol(metaclass=ABCMeta):
    avilla: Avilla
    platform: ClassVar[Platform]
    message_serializer: MessageSerializer
    message_deserializer: MessageDeserializer

    completion_rules: ClassVar[dict[str, dict[str, str]]] = cast(dict, MappingProxyType({}))
    action_middlewares: list[ActionMiddleware] = []

    event_parser: ClassVar[AbstractEventParser]
    action_executors: ClassVar[list[type[ProtocolActionExecutor]]] = cast(list, ())
    # 顺序严格, 建议 full > exist long > exist short > any|none
    resource_providers: ClassVar[dict[Selector, type[ProtocolResourceProvider]]] = cast(dict, MappingProxyType({}))
    metadata_providers: ClassVar[list[type[ProtocolMetadataSource]]] = cast(list, ())
    query_handlers: ClassVar[list[type[ProtocolAbstractQueryHandler]]] = cast(list, ())
    extension_impls: ClassVar[dict[type[ActionExtension], ActionExtensionImpl]] = cast(dict, MappingProxyType({}))

    def __init__(self):
        ...

    @property
    def land(self):
        return self.platform[Land]

    @property
    def abstract(self):
        return self.platform[Abstract]

    @property
    def resource_labels(self) -> set[str]:
        return {pattern.path_without_land for pattern in self.resource_providers.keys()}

    @abstractmethod
    def ensure(self, avilla: Avilla) -> Any:
        ...

    def get_accounts(self, selector: Selector | None = None) -> list[AbstractAccount]:
        return self.avilla.get_accounts(selector=selector, land=self.platform[Land])

    def get_account(self, selector: Selector) -> AbstractAccount | None:
        return self.avilla.get_account(selector=selector, land=self.platform[Land])

    def get_resource_provider(self, resource: Selector) -> ResourceProvider | None:
        for pattern, provider_class in self.resource_providers.items():
            if pattern.match(resource):
                return provider_class(self)

    async def parse_message(self, data: Any) -> MessageChain:
        return MessageChain(await self.message_deserializer.parse_sentence(self, data))

    async def serialize_message(self, message: MessageChain) -> Any:
        return await self.message_serializer.serialize_chain(self, message)

    def get_metadata_provider(self, target: Selector | str) -> MetadataSource | None:
        if isinstance(target, Selector):
            target = target.path_without_land
        for source in self.metadata_providers:
            if source.pattern == target:
                return source(self)

    def post_event(self, event: AvillaEvent):
        with ExitStack() as stack:
            stack.enter_context(ctx_avilla.use(self.avilla))
            stack.enter_context(ctx_protocol.use(self))
            self.avilla.broadcast.postEvent(event)
