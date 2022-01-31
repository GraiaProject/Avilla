from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Generic,
    Optional,
    TypeVar,
    Union,
    overload,
)

if TYPE_CHECKING:
    from avilla.core.selectors import entity as entity_selector
    from avilla.core.service import Service


@dataclass
class Status:
    available: bool
    description: str


R = TypeVar("R")
TCallback = TypeVar("TCallback", bound=Callable)
TService = TypeVar("TService", bound="Service")


class ExportInterface(Generic[TService]):
    service: TService
    current: Optional["entity_selector"] = None

    if TYPE_CHECKING:

        @overload
        def get_status(self) -> Dict["entity_selector", Status]:
            pass

        @overload
        def get_status(self, entity: "entity_selector") -> Status:
            pass

    def set_current(self, entity: "entity_selector") -> None:
        self.current = entity

    def get_status(self, entity: "entity_selector" = None) -> Union[Status, Dict["entity_selector", Status]]:
        if entity is not None:
            return self.service.get_status(entity)
        return self.service.get_status()

    def get_current_status(self) -> Status:
        if self.current is None:
            raise ValueError("uncertain entity, it's a anonymous interface!")
        return self.get_status(self.current)

    def set_status(self, entity: "entity_selector", available: bool, description: str) -> None:
        self.service.set_status(entity, available, description)

    def set_current_status(self, available: bool, description: str) -> None:
        if self.current is None:
            raise ValueError("uncertain entity, it's a anonymous interface!")
        self.set_status(self.current, available, description)
