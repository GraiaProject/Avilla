import asyncio
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
from avilla.core.service.entity import ExportInterface, Status

TInterface = TypeVar("TInterface", bound=ExportInterface)
TCallback = TypeVar("TCallback", bound=Callable)

if TYPE_CHECKING:
    from avilla.core.selectors import entity as entity_selector


class Service(metaclass=ABCMeta):
    supported_interface_types: ClassVar[
        Union[
            Set[Type[ExportInterface]],
            Dict[Type[ExportInterface], Union[int, float]],
            Tuple[Union[Set[Type[ExportInterface]], Dict[Type[ExportInterface], Union[int, float]]], ...],
        ]
    ]

    status: Dict["entity_selector", Status]

    def __init__(self) -> None:
        self.status = {}

    @abstractmethod
    def get_interface(self, interface_type: Type[TInterface]) -> TInterface:
        pass

    @abstractmethod
    @overload
    def get_status(self) -> Dict["entity_selector", Status]:
        pass

    @abstractmethod
    @overload
    def get_status(self, entity: "entity_selector") -> Status:
        pass

    if TYPE_CHECKING:

        @abstractmethod
        def get_status(
            self, entity: "entity_selector" = None
        ) -> Union[Status, Dict[entity_selector, Status]]:
            pass

    def set_status(self, entity: "entity_selector", available: bool, description: str) -> None:
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

    available_waiters: Dict["entity_selector", asyncio.Event]

    async def wait_for_available(self, target: "entity_selector"):
        status = self.get_status(target)
        if status.available:
            return
        try:
            await self.available_waiters.setdefault(target, asyncio.Event()).wait()
        finally:
            self.available_waiters.pop(target, None)

    def trig_available_waiters(self, target: "entity_selector"):
        if target in self.available_waiters:
            self.available_waiters[target].set()
