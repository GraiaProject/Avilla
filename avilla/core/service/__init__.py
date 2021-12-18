from abc import ABCMeta, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    List,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from avilla.core.launch import LaunchComponent
from avilla.core.selectors import entity as entity_selector
from avilla.core.service.entity import BehaviourDescription, ExportInterface, Status

TInterface = TypeVar("TInterface", bound=ExportInterface)
TCallback = TypeVar("TCallback", bound=Callable)


class Service(metaclass=ABCMeta):
    supported_interface_types: ClassVar[Set[Type[ExportInterface]]]
    supported_description_types: ClassVar[Set[Type[BehaviourDescription]]]

    status: Dict[entity_selector, Status]
    cb: List[Tuple[Union[Type[BehaviourDescription], BehaviourDescription], Callable[..., Any]]]

    @abstractmethod
    def get_interface(self, interface_type: Type[TInterface]) -> TInterface:
        pass

    @abstractmethod
    @overload
    def get_status(self) -> Dict[entity_selector, Status]:
        pass

    @abstractmethod
    @overload
    def get_status(self, entity: entity_selector) -> Status:
        pass

    if TYPE_CHECKING:

        @abstractmethod
        def get_status(self, entity: entity_selector = None) -> Union[Status, Dict[entity_selector, Status]]:
            pass

    def set_status(self, entity: entity_selector, available: bool, description: str) -> None:
        for k, v in self.status.items():
            if k & entity:
                v.available = available
                v.description = description
                return
        self.status[entity] = Status(available, description)

    @property
    @abstractmethod
    def launch_component(self) -> LaunchComponent:
        pass

    def expand(
        self, behaviour: Union[Type[BehaviourDescription[TCallback]], BehaviourDescription[TCallback]]
    ):
        def decorator(callback: TCallback):
            self.cb.append((behaviour, callback))
            return callback

        return decorator

    def expand_behaviour(
        self,
        behaviour: Union[Type[BehaviourDescription[TCallback]], BehaviourDescription[TCallback]],
        callback: TCallback,
    ) -> None:
        self.cb.append((behaviour, callback))
