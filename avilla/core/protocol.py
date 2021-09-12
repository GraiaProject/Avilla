from abc import ABCMeta, abstractmethod
from contextlib import AsyncExitStack
from typing import TYPE_CHECKING, Any, Dict, Generic, Tuple, Type, Union

from avilla.core.builtins.profile import SelfProfile
from avilla.core.contactable import Contactable
from avilla.core.message.chain import MessageChain
from avilla.core.network.client import Client
from avilla.core.network.service import Service
from avilla.core.network.signatures import (ClientCommunicationMethod,
                                            ServiceCommunicationMethod)
from avilla.core.platform import Platform
from avilla.core.relationship import Relationship
from avilla.core.typing import T_Config, T_ExecMW, T_Profile

from .execution import Execution

if TYPE_CHECKING:
    from . import Avilla


class BaseProtocol(Generic[T_Config], metaclass=ABCMeta):
    avilla: "Avilla"
    config: T_Config
    using_networks: Dict[str, Union[Client, Service]]
    using_exec_method: Union[Type[ClientCommunicationMethod], Type[ServiceCommunicationMethod]]

    platform: Platform = Platform(
        name="Avilla Universal Protocol Implementation",
        protocol_provider_name="Avilla Protocol",
        implementation="avilla-core",
        supported_impl_version="$any",
        generation="1",
    )

    def __init__(self, avilla: "Avilla", config: T_Config) -> None:
        self.avilla = avilla
        self.config = config
        self.using_networks, self.using_exec_method = self.ensure_networks()
        self.__post_init__()

    @abstractmethod
    def ensure_networks(
        self,
    ) -> Tuple[
        Dict[str, Union[Client, Service]],
        Union[Type[ClientCommunicationMethod], Type[ServiceCommunicationMethod]],
    ]:
        raise NotImplementedError

    def __post_init__(self) -> None:
        pass

    def ensure_execution(self, execution: "Execution") -> Any:
        raise NotImplementedError

    @abstractmethod
    def get_self(self) -> "Contactable[SelfProfile]":
        raise NotImplementedError

    @abstractmethod
    async def parse_message(self, data: Any) -> "MessageChain":
        raise NotImplementedError

    @abstractmethod
    async def serialize_message(self, message: "MessageChain") -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_relationship(self, entity: "Contactable[T_Profile]") -> "Relationship[T_Profile]":
        return Relationship(entity, self, middlewares=self.avilla.middlewares)

    @abstractmethod
    async def launch_entry(self):  # maybe need change.
        raise NotImplementedError

    def has_ability(self, ability: str) -> bool:
        raise NotImplementedError

    async def exec_directly(self, execution: Execution, *middlewares: T_ExecMW) -> Any:
        async with AsyncExitStack() as exit_stack:
            for middleware in middlewares:
                await exit_stack.enter_async_context(middleware(self, execution))  # type: ignore
            return await self.ensure_execution(execution)
