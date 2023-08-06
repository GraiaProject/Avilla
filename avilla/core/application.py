from __future__ import annotations

import asyncio
import signal
from collections import ChainMap
from typing import TYPE_CHECKING, Iterable, TypeVar

from creart import it
from launart import Launart
from launart.service import Service

from avilla.core._runtime import get_current_avilla
from avilla.core.account import AccountInfo
from avilla.core.dispatchers import AvillaBuiltinDispatcher
from avilla.core.protocol import BaseProtocol
from avilla.core.ryanvk import Isolate
from avilla.core.ryanvk.staff import Staff
from avilla.core.selector import Selector
from avilla.core.service import AvillaService
from avilla.core.utilles import identity
from graia.broadcast import Broadcast

if TYPE_CHECKING:
    from avilla.core.ryanvk.protocol import SupportsArtifacts
    from graia.broadcast import Decorator, Dispatchable, Namespace, T_Dispatcher

    from .resource import Resource

T = TypeVar("T")
TP = TypeVar("TP", bound=BaseProtocol)


class Avilla:
    broadcast: Broadcast
    launch_manager: Launart
    protocols: list[BaseProtocol]
    accounts: dict[Selector, AccountInfo]
    service: AvillaService
    isolate: Isolate

    def __init__(
        self,
        *,
        broadcast: Broadcast | None = None,
        launch_manager: Launart | None = None,
        message_cache_size: int = 300,
    ):
        self.broadcast = broadcast or it(Broadcast)
        self.launch_manager = launch_manager or Launart()
        self.protocols = []
        self._protocol_map = {}
        self.accounts = {}

        self.service = AvillaService(self, message_cache_size)
        self.isolate = Isolate()

        self.launch_manager.add_component(self.service)
        self.broadcast.finale_dispatchers.append(AvillaBuiltinDispatcher(self))

        self.__init_isolate__()

        if message_cache_size > 0:
            from avilla.core.context import Context
            from avilla.core.message import Message
            from avilla.standard.core.account import AccountUnregistered
            from avilla.standard.core.message import MessageReceived

            @self.broadcast.receiver(MessageReceived)
            async def message_cacher(context: Context, message: Message):
                if context.account.info.enabled_message_cache:
                    self.service.message_cache[context.account.route].push(message)

            @self.broadcast.receiver(AccountUnregistered)
            async def clear_cache(event: AccountUnregistered):
                if event.account.route in self.service.message_cache:
                    del self.service.message_cache[event.account.route]

            message_cacher.__annotations__ = {"context": Context, "message": Message}
            clear_cache.__annotations__ = {"event": AccountUnregistered}

    def __init_isolate__(self):
        from avilla.core.builtins.resource_fetch import CoreResourceFetchPerform

        self.isolate.apply(CoreResourceFetchPerform)

    def get_staff_components(self) -> dict[str, SupportsArtifacts]:
        return {"avilla": self}

    def get_staff_artifacts(self):
        return ChainMap(self.isolate.artifacts)

    def __staff_generic__(self, element_type: dict, event_type: dict):
        ...

    @classmethod
    def current(cls):
        return get_current_avilla()

    async def fetch_resource(self, resource: Resource[T]) -> T:
        return await Staff.focus(self).fetch_resource(resource)

    def _update_protocol_map(self):
        self._protocol_map = {type(i): i for i in self.protocols}

    def apply_protocols(self, *protocols: BaseProtocol) -> None:
        self.protocols.extend(protocols)
        self._update_protocol_map()

        for protocol in protocols:
            protocol.ensure(self)

    def get_protocol(self, protocol_type: type[TP]) -> TP:
        if protocol_type not in self._protocol_map:
            raise ValueError(f"{identity(protocol_type)} is unregistered on this Avilla instance")

        return self._protocol_map[protocol_type]  # type: ignore

    def apply_services(self, *services: Service):
        for i in services:
            self.launch_manager.add_component(i)

    def listen(
        self,
        event: type[Dispatchable],
        priority: int = 16,
        dispatchers: list[T_Dispatcher] | None = None,
        namespace: Namespace | None = None,
        decorators: list[Decorator] | None = None,
    ):
        return self.broadcast.receiver(event, priority, dispatchers, namespace, decorators)

    def launch(
        self,
        *,
        loop: asyncio.AbstractEventLoop | None = None,
        stop_signal: Iterable[signal.Signals] = (signal.SIGINT,),
    ):
        self.launch_manager.launch_blocking(loop=loop, stop_signal=stop_signal)
