from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, Generic, List, Tuple, Type, TypeVar, Union, cast

from avilla.core.service.entity import Activity, BehaviourDescription


if TYPE_CHECKING:
    from avilla.core.service import Service
    from avilla.core.service.entity import ExportInterface

TActivityHandler = Callable[[Union[Activity, None]], Awaitable]
TCallback = TypeVar("TCallback", bound=Callable)
TInterface = TypeVar("TInterface", bound="ExportInterface")

class BehaviourSession(Generic[TInterface]):
    service: Service
    interface: TInterface
    activity_handlers: Dict[Type[Activity], TActivityHandler]

    cb: List[Tuple[Union[Type[BehaviourDescription], BehaviourDescription], Callable[..., Any]]]

    def __init__(
        self,
        service: Service,
        interface: TInterface,
        activity_handlers: Dict[Type[Activity], TActivityHandler],
    ) -> None:
        self.service = service
        self.interface = interface
        self.activity_handlers = activity_handlers

    async def execute(self, activity: Union[Type[Activity], Activity]):
        activity_class = activity if isinstance(activity, type) else type(activity)
        handler = self.activity_handlers.get(activity_class)
        if handler is None:
            raise NotImplementedError(f"No handler for activity {activity_class}")
        return await handler(activity if not isinstance(activity, type) else None)

    def update_activity_handlers(self, activity_handlers: Dict[Type[Activity], TActivityHandler], clean: bool = False):
        if clean:
            self.activity_handlers.clear()
        self.activity_handlers.update(activity_handlers)

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

    def submit_behaviour_expansion(self):
        for behaviour, callback in self.cb:
            self.interface.expand_behaviour(behaviour, callback)

    def get_behaviour_cbs(self, behaviour_type: Type[BehaviourDescription[TCallback]]) -> List[TCallback]:
        return cast(List[TCallback], [callback for behaviour, callback in self.cb if behaviour is behaviour_type or isinstance(behaviour, behaviour_type)])

    