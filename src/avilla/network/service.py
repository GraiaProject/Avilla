import abc
from typing import Any, Callable, Dict, Generic, List, TypeVar

from avilla.utilles.translator import OriginProvider

T_Connection = TypeVar("T_Connection")

class Service(Generic[T_Connection], abc.ABC):
    connections: Dict[str, T_Connection]

    cb_connection_created: Dict[str, List[Callable[[str, T_Connection], None]]]
    cb_connection_destroyed: Dict[str, List[Callable[[str], None]]]
    cb_data_received: Dict[str, List[Callable[['Service', str, bytes], None]]]

    @abc.abstractmethod
    async def launchEntry(self): ...

    @abc.abstractmethod
    async def call(self, connection_id: str, endpoint: str, data: Any) -> OriginProvider[bytes]: ...

    def on_connect(self, connection_id: str):
        def wrapper(func: Callable[[str, T_Connection], Any]): # id, ctx.
            self.cb_connection_created[connection_id].append(func)
            return func
        return wrapper
    
    def on_disconnect(self, connection_id: str):
        def wrapper(func: Callable[[str], None]):
            self.cb_connection_destroyed[connection_id].append(func)
            return func
        return wrapper
    
    def on_data_received(self, connection_id: str):
        def wrapper(func: Callable[['Service', str, bytes], None]):
            self.cb_data_received[connection_id].append(func)
            return func
        return wrapper