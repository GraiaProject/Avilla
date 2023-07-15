from __future__ import annotations

from collections import ChainMap
from typing import TYPE_CHECKING, TypeVar

from avilla.core._runtime import get_current_avilla
from avilla.core.account import AccountInfo
from avilla.core.dispatchers import AvillaBuiltinDispatcher
from avilla.core.protocol import BaseProtocol
from avilla.core.ryanvk import Isolate
from avilla.core.ryanvk.staff import Staff
from avilla.core.selector import Selector
from avilla.core.service import AvillaService
from graia.broadcast import Broadcast
from launart import Launart

if TYPE_CHECKING:
    from avilla.core.ryanvk.protocol import SupportsArtifacts

    from .resource import Resource

T = TypeVar("T")


class Avilla:
    broadcast: Broadcast
    launch_manager: Launart
    protocols: list[BaseProtocol]
    accounts: dict[Selector, AccountInfo]
    service: AvillaService
    isolate: Isolate

    def __init__(
        self,
        broadcast: Broadcast,
        launch_manager: Launart,
        protocols: list[BaseProtocol],
        message_cache_size: int = 300,
    ):
        if len({type(i) for i in protocols}) != len(protocols):
            raise ValueError("protocol must be unique, and the config should be passed by config.")

        self.broadcast = broadcast
        self.launch_manager = launch_manager
        self.protocols = protocols
        self._protocol_map = {type(i): i for i in protocols}
        self.accounts = {}
        self.service = AvillaService(self, message_cache_size)
        self.isolate = Isolate()

        self.launch_manager.add_component(self.service)

        for protocol in self.protocols:
            # Ensureable 用于注册各种东西，包括 Service, ResourceProvider 等。
            protocol.ensure(self)

        self.broadcast.finale_dispatchers.append(AvillaBuiltinDispatcher(self))

        self.__init_isolate__()

        if message_cache_size > 0:
            from avilla.core.context import Context
            from avilla.core.message import Message
            from avilla.standard.core.message import MessageReceived

            @broadcast.receiver(MessageReceived)
            async def message_cacher(context: Context, message: Message):
                if context.account.info.enabled_message_cache:
                    self.service.message_cache[context.account.route].push(message)

    @classmethod
    def current(cls) -> "Avilla":
        return get_current_avilla()

    @property
    def loop(self):
        return self.broadcast.loop

    async def fetch_resource(self, resource: Resource[T]) -> T:
        return await Staff(self).fetch_resource(resource)

    def __init_isolate__(self):
        from avilla.core.builtins.resource_fetch import CoreResourceFetchPerform

        self.isolate.apply(CoreResourceFetchPerform)

    def get_staff_components(self) -> dict[str, SupportsArtifacts]:
        # 我确信这是个 pyright 的 bug, 把这个 return_type 去掉就来了。
        return {"avilla": self}

    def get_staff_artifacts(self):
        return ChainMap(self.isolate.artifacts)

    def __staff_generic__(self, element_type: dict, event_type: dict):
        ...
