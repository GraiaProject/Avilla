from abc import ABCMeta, abstractmethod, abstractstaticmethod
from functools import singledispatchmethod
from typing import TYPE_CHECKING, Any, AsyncIterable, Dict, Generic, Iterable, Literal, Tuple, Type, TypeVar, Union

from avilla.builtins.profile import SelfProfile
from avilla.entity import Entity
from avilla.group import Group
from avilla.message.chain import MessageChain
from avilla.network.client import Client
from avilla.network.service import Service
from avilla.network.signatures import ClientCommunicationMethod, ServiceCommunicationMethod
from avilla.profile import BaseProfile
from avilla.relationship import Relationship

from .execution import Execution

if TYPE_CHECKING:
    from . import Avilla

T_Config = TypeVar("T_Config")
T_Profile = TypeVar("T_Profile")


class BaseProtocol(Generic[T_Config], metaclass=ABCMeta):
    avilla: "Avilla"
    config: T_Config
    using_networks: Dict[str, Union[Client, Service]]
    using_exec_method: Union[Type[ClientCommunicationMethod], Type[ServiceCommunicationMethod]]

    def __init__(self, avilla: "Avilla", config: T_Config) -> None:
        self.avilla = avilla
        self.config = config
        self.using_networks, self.using_exec_method = self.ensureNetworks()
        self.__post_init__()

    @abstractstaticmethod
    def ensureNetworks(
        self, avilla: "Avilla"
    ) -> Tuple[
        Dict[str, Union[Client, Service]], Union[Type[ClientCommunicationMethod], Type[ServiceCommunicationMethod]]
    ]:
        raise NotImplementedError

    def __post_init__(self) -> None:
        pass

    @singledispatchmethod  # 用util里的那个东西生成一个吧.
    def ensureExecution(self, relationship: Relationship, execution: "Execution") -> Any:
        raise NotImplementedError

    @abstractmethod
    def getSelf(self) -> "Entity[SelfProfile]":
        raise NotImplementedError

    @abstractmethod
    async def getMembers(self, group: Group[Any]) -> "Iterable[Entity[Union[SelfProfile, BaseProfile]]]":
        raise NotImplementedError

    @abstractmethod
    async def parseMessage(self, data: Any) -> "MessageChain":
        raise NotImplementedError

    @abstractmethod
    async def serializeMessage(self, message: "MessageChain") -> Any:
        raise NotImplementedError

    @abstractmethod
    def getRelationship(self, entity: "Entity[T_Profile]") -> "Relationship[T_Profile, Any, BaseProtocol]":
        raise NotImplementedError

    @abstractmethod
    async def launchEntry(self):  # maybe need change.
        raise NotImplementedError
