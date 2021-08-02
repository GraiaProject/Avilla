from abc import ABCMeta, abstractmethod, abstractstaticmethod
from typing import TYPE_CHECKING, Any, Dict, Generic, Iterable, Tuple, Type, Union

from avilla.builtins.profile import SelfProfile
from avilla.entity import Entity
from avilla.group import Group
from avilla.message.chain import MessageChain
from avilla.network.client import Client
from avilla.network.service import Service
from avilla.network.signatures import ClientCommunicationMethod, ServiceCommunicationMethod
from avilla.profile import BaseProfile
from avilla.relationship import Relationship
from avilla.typing import T_Config, T_Profile

from .execution import Execution

if TYPE_CHECKING:
    from . import Avilla


class BaseProtocol(Generic[T_Config], metaclass=ABCMeta):
    avilla: "Avilla"
    config: T_Config
    using_networks: Dict[str, Union[Client, Service]]
    using_exec_method: Union[Type[ClientCommunicationMethod], Type[ServiceCommunicationMethod]]

    def __init__(self, avilla: "Avilla", config: T_Config) -> None:
        self.avilla = avilla
        self.config = config
        self.using_networks, self.using_exec_method = self.ensure_networks()
        self.__post_init__()

    @abstractstaticmethod
    def ensure_networks(
        self,
    ) -> Tuple[
        Dict[str, Union[Client, Service]],
        Union[Type[ClientCommunicationMethod], Type[ServiceCommunicationMethod]],
    ]:
        raise NotImplementedError

    def __post_init__(self) -> None:
        pass

    def ensure_execution(self, relationship: Relationship, execution: "Execution") -> Any:
        raise NotImplementedError

    @abstractmethod
    def get_self(self) -> "Entity[SelfProfile]":
        raise NotImplementedError

    @abstractmethod
    async def get_members(self, group: Group[Any]) -> "Iterable[Entity[Union[SelfProfile, BaseProfile]]]":
        raise NotImplementedError

    @abstractmethod
    async def parse_message(self, data: Any) -> "MessageChain":
        raise NotImplementedError

    @abstractmethod
    async def serialize_message(self, message: "MessageChain") -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_relationship(
        self, entity: "Entity[T_Profile]"
    ) -> "Relationship[T_Profile, Any, BaseProtocol]":
        raise NotImplementedError

    @abstractmethod
    async def launch_entry(self):  # maybe need change.
        raise NotImplementedError
