from dataclasses import dataclass
from inspect import isclass
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from avilla.core.selectors import entity as entity_selector

if TYPE_CHECKING:
    from avilla.core.service import Service


@dataclass
class Status:
    available: bool
    description: str


R = TypeVar("R")
TCallback = TypeVar("TCallback", bound=Callable)
TService = TypeVar("TService", bound="Service")


class Activity(Generic[R]):
    pass


class BehaviourDescription(Generic[TCallback]):
    pass


class ExportInterface(Generic[TService]):
    service: TService
    current: Optional[entity_selector] = None

    behaviours: List[Tuple[Union[Type[BehaviourDescription], BehaviourDescription], Callable[..., Any]]]

    if TYPE_CHECKING:

        @overload
        def get_status(self) -> Dict[entity_selector, Status]:
            pass

        @overload
        def get_status(self, entity: entity_selector) -> Status:
            pass

    def get_status(self, entity: entity_selector = None) -> Union[Status, Dict[entity_selector, Status]]:
        if entity is not None:
            return self.service.get_status(entity)
        return self.service.get_status()

    def get_current_status(self) -> Status:
        if self.current is None:
            raise ValueError("uncertain entity, it's a anonymous interface!")
        return self.get_status(self.current)

    def set_status(self, entity: entity_selector, available: bool, description: str) -> None:
        self.service.set_status(entity, available, description)

    def set_current_status(self, available: bool, description: str) -> None:
        if self.current is None:
            raise ValueError("uncertain entity, it's a anonymous interface!")
        self.set_status(self.current, available, description)

    @property
    def supported_description_types(self):
        return self.service.supported_description_types

    def get_behaviours(self, behaviour: Type[BehaviourDescription[TCallback]]) -> List[TCallback]:
        return cast(
            List[TCallback],
            [
                callback
                for behaviour_, callback in self.behaviours
                if isinstance(behaviour, behaviour_ if isclass(behaviour_) else behaviour_.__class__)  # type: ignore
            ],
        )

    def expand(
        self, behaviour: Union[Type[BehaviourDescription[TCallback]], BehaviourDescription[TCallback]]
    ):
        def decorator(callback: TCallback):
            self.behaviours.append((behaviour, callback))
            return callback

        return decorator

    def expand_behaviour(
        self,
        behaviour: Union[Type[BehaviourDescription[TCallback]], BehaviourDescription[TCallback]],
        callback: TCallback,
    ) -> None:
        self.behaviours.append((behaviour, callback))
