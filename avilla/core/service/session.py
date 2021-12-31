import asyncio
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
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

from graia.broadcast.utilles import run_always_await_safely

from avilla.core.service.entity import Activity, BehaviourDescription

if TYPE_CHECKING:
    from avilla.core.service import Service
    from avilla.core.service.entity import ExportInterface

TActivityHandler = Callable[[Union[Activity, None]], Union[Awaitable[Any], Any]]
TCallback = TypeVar("TCallback", bound=Callable)
TInterface = TypeVar("TInterface", bound="ExportInterface")


class BehaviourSession(Generic[TInterface]):
    service: "Service"
    interface: TInterface
    activity_handlers: Dict[Type[Activity], TActivityHandler]

    cbs: List[Tuple[Union[Type[BehaviourDescription], BehaviourDescription], Callable[..., Any]]]
    cb_remover: Optional[Callable[[Type[BehaviourDescription], Callable[..., Any]], None]] = None
    prepared_signal: Optional[asyncio.Event] = None

    def __init__(
        self,
        service: "Service",
        interface: TInterface,
        activity_handlers: Dict[Type[Activity], TActivityHandler],
        prepared_signal: asyncio.Event = None,
        cb_remover: Optional[Callable[..., Any]] = None,
    ) -> None:
        self.service = service
        self.interface = interface
        self.activity_handlers = activity_handlers
        self.cbs = []
        self.prepared_signal = prepared_signal
        self.cb_remover = cb_remover

    if TYPE_CHECKING:
        R = TypeVar("R")

        @overload
        async def execute(self, activity: Type[Activity[R]]) -> R:
            pass

        @overload
        async def execute(self, activity: Activity[R]) -> R:
            pass

        async def execute(self, activity: ...) -> Any:
            ...

    else:

        async def execute(self, activity: Union[Type[Activity], Activity]):
            activity_class = activity if isinstance(activity, type) else type(activity)
            handler = self.activity_handlers.get(activity_class)
            if handler is None:
                raise NotImplementedError(f"No handler for activity {activity_class}")
            return await run_always_await_safely(
                handler, activity if not isinstance(activity, type) else None
            )

    async def execute_all(self, *activities: Union[Type[Activity], Activity]):
        return await asyncio.gather(*[self.execute(activity) for activity in activities])

    if not TYPE_CHECKING:

        def update_activity_handlers(
            self, activity_handlers: Dict[Type[Activity], TActivityHandler], clean: bool = False
        ):
            if clean:
                self.activity_handlers.clear()
            self.activity_handlers.update(activity_handlers)

    else:
        _T = TypeVar("_T")

        def update_activity_handlers(
            self,
            activity_handlers: Dict[Type[_T], Callable[[Union[_T, None]], Union[Awaitable[Any], Any]]],
            clean: bool = False,
        ):
            ...

    def expand(
        self, behaviour: Union[Type[BehaviourDescription[TCallback]], BehaviourDescription[TCallback]]
    ):
        def decorator(callback: TCallback):
            self.cbs.append((behaviour, callback))
            return callback

        return decorator

    def expand_behaviour(
        self,
        behaviour: Union[Type[BehaviourDescription[TCallback]], BehaviourDescription[TCallback]],
        callback: TCallback,
    ) -> None:
        self.cbs.append((behaviour, callback))

    def submit_behaviour_expansion(
        self,
        cb: Callable[[Union[Type[BehaviourDescription], BehaviourDescription], Callable[..., Any]], None],
    ):
        for behaviour, callback in self.cbs:
            cb(behaviour, callback)

    def remove_callback(self, behaviour: Type[BehaviourDescription], cb: Callable[..., Any]) -> None:
        if not self.cb_remover:
            raise RuntimeError("cb_remover is not set")
        self.cb_remover(behaviour, cb)

    def get_behaviour_cbs(self, behaviour_type: Type[BehaviourDescription[TCallback]]) -> List[TCallback]:
        return cast(
            List[TCallback],
            [
                callback
                for behaviour, callback in self.cbs
                if behaviour is behaviour_type or isinstance(behaviour, behaviour_type)
            ],
        )

    def prepared(self):
        if self.prepared_signal is not None:
            self.prepared_signal.set()

    if TYPE_CHECKING:
        T = TypeVar("T")

    async def wait(
        self,
        behaviour: Union[Type[BehaviourDescription], BehaviourDescription],
        fetcher: Callable[..., "T"] = lambda *x: x[-1],
    ) -> "T":
        behaviour_type = behaviour if isinstance(behaviour, type) else type(behaviour)
        fut = asyncio.get_running_loop().create_future()

        async def value_getter(*args):
            fut.set_result(fetcher(*args))

        self.expand_behaviour(behaviour, value_getter)
        try:
            return await fut
        finally:
            self.remove_callback(behaviour_type, value_getter)

    def is_allowed(self, activity_type: Type[Activity]) -> bool:
        return activity_type in self.activity_handlers
