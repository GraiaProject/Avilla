from abc import abstractmethod, ABCMeta
from functools import singledispatchmethod
from typing import Any, Iterable, Generic, TYPE_CHECKING, TypeVar, Union
from avilla.builtins.profile import SelfProfile
from avilla.entity import Entity
from avilla.group import Group
from avilla.message.chain import MessageChain
from avilla.profile import BaseProfile

from avilla.relationship import Relationship
from .execution import Execution

if TYPE_CHECKING:
    from . import Avilla

T_Config = TypeVar('T_Config')
T_Profile = TypeVar('T_Profile')

class BaseProtocol(Generic[T_Config], metaclass=ABCMeta):
    avilla: "Avilla"
    config: T_Config

    def __init__(self, avilla: "Avilla", config: T_Config) -> None:
        self.avilla = avilla
        self.config = config

    @singledispatchmethod
    def ensureExecution(self, relationship: Relationship, execution: 'Execution') -> Any:
        raise NotImplementedError
    
    @staticmethod
    def gen_ensure_execution_method():
        @singledispatchmethod
        def ensureExecution(self, relationship: Relationship, execution: 'Execution') -> Any:
            raise NotImplementedError
        return ensureExecution
    
    @abstractmethod
    def getSelf(self) -> 'Entity[SelfProfile]':
        raise NotImplementedError
    
    @abstractmethod
    def getMembers(self, group: Group[Entity[T_Profile, Any]]) -> 'Iterable[Entity[Union[SelfProfile, BaseProfile]]]':
        raise NotImplementedError
    
    @abstractmethod
    async def parseMessage(self, data: Any) -> 'MessageChain':
        raise NotImplementedError
    
    @abstractmethod
    async def serializeMessage(self, message: 'MessageChain') -> Any:       
        raise NotImplementedError
    
    @abstractmethod
    def getRelationship(self, entity: 'Entity[T_Profile]') -> "Relationship[T_Profile, Any, BaseProtocol]":       
        raise NotImplementedError
    
    @abstractmethod
    async def launchEntry(self): # maybe need change.
        raise NotImplementedError

