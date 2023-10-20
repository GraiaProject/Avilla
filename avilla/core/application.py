from __future__ import annotations

import asyncio
import signal
from typing import TYPE_CHECKING, Any, Iterable, TypeVar, overload

from creart import it
from launart import Launart
from launart.service import Service
from loguru import logger

from avilla.core._runtime import get_current_avilla
from avilla.core.account import AccountInfo, BaseAccount
from avilla.core.dispatchers import AvillaBuiltinDispatcher
from avilla.core.protocol import BaseProtocol
from avilla.core.ryanvk.staff import Staff
from avilla.core.selector import Selector
from avilla.core.service import AvillaService
from avilla.core.utilles import identity
from graia.amnesia.builtins.memcache import MemcacheService
from graia.broadcast import Broadcast

if TYPE_CHECKING:
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
    global_artifacts: dict[Any, Any]

    def __init__(
        self,
        *,
        broadcast: Broadcast | None = None,
        launch_manager: Launart | None = None,
        message_cache_size: int = 300,
        record_send: bool = True,
    ):
        self.broadcast = broadcast or it(Broadcast)
        self.launch_manager = launch_manager or it(Launart)
        self.protocols = []
        self._protocol_map = {}
        self.accounts = {}

        self.service = AvillaService(self, message_cache_size)
        self.global_artifacts = {}

        self.launch_manager.add_component(MemcacheService())
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

        if record_send:
            from avilla.core.context import Context
            from avilla.core.message import Message
            from avilla.standard.core.message import MessageSent

            @self.broadcast.receiver(MessageSent)
            async def message_sender(context: Context, message: Message):
                scene = f"{'.'.join(f'{k}({v})' for k, v in context.scene.items())}"
                logger.info(
                    f"[{context.account.info.protocol.__class__.__name__.replace('Protocol', '')} "
                    f"{context.account.route['account']}]: "
                    f"{scene} <- {str(message.content)!r}"
                )

            message_sender.__annotations__ = {"context": Context, "message": Message}

    def __init_isolate__(self):
        from avilla.core.builtins.resource_fetch import CoreResourceFetchPerform

        CoreResourceFetchPerform.apply_to(self.global_artifacts)

    def get_staff_components(self):
        return {"avilla": self}

    def get_staff_artifacts(self):
        return [self.global_artifacts]

    def __staff_generic__(self, element_type: dict, event_type: dict):
        ...

    @classmethod
    def current(cls):
        return get_current_avilla()

    async def fetch_resource(self, resource: Resource[T]) -> T:
        return await Staff(self.get_staff_artifacts(), self.get_staff_components()).fetch_resource(resource)

    def get_account(self, target: Selector) -> AccountInfo:
        return self.accounts[target]

    @overload
    def get_accounts(self, *, land: str) -> list[AccountInfo]:
        ...

    @overload
    def get_accounts(self, *, pattern: str) -> list[AccountInfo]:
        ...

    @overload
    def get_accounts(self, *, protocol_type: type[BaseProtocol]) -> list[AccountInfo]:
        ...

    @overload
    def get_accounts(self, *, account_type: type[BaseAccount]) -> list[AccountInfo]:
        ...

    def get_accounts(
        self,
        *,
        land: str | None = None,
        pattern: str | None = None,
        protocol_type: type[BaseProtocol] | None = None,
        account_type: type[BaseAccount] | None = None,
    ) -> list[AccountInfo]:
        if land:
            return [account for account in self.accounts.values() if account.platform.land.name == land]
        if pattern:
            return [account for selector, account in self.accounts.items() if selector.follows(pattern)]
        if protocol_type:
            return [account for account in self.accounts.values() if isinstance(account.protocol, protocol_type)]
        if account_type:
            return [account for account in self.accounts.values() if isinstance(account.account, account_type)]
        raise ValueError("No filter is specified")

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
