# TODO: remake

import abc
from typing import TYPE_CHECKING, Any, Callable, Dict, Generic, List, Optional

from avilla.network.signatures import ServiceCommunicationMethod
from avilla.typing import T_Connection
from avilla.utilles.transformer import OriginProvider

if TYPE_CHECKING:
    from avilla import Avilla


class Service(Generic[T_Connection], abc.ABC):
    connections: Dict[str, T_Connection]

    cbp_connection_created: Dict[str, List[Callable[[str, T_Connection], None]]]
    cbp_data_received: Dict[str, List[Callable[["Service", str, OriginProvider[bytes]], None]]]
    cbp_connection_destroyed: Dict[str, List[Callable[[str], None]]]

    def __init__(self) -> None:
        self.cb_connection_created = {}
        self.cb_connection_destroyed = {}
        self.cb_data_received = {}

    def has(self, connection_id: str):
        return connection_id in self.connections

    @abc.abstractmethod
    async def launch_entry(
        self, avilla: "Avilla", config: Optional[ServiceCommunicationMethod] = None
    ):
        ...

    @abc.abstractmethod
    async def send(self, connection_id: str, data: bytes):
        ...

    def register_on_connect(self, connection_id: str):
        def wrapper(func: Callable[[str, T_Connection], Any]):  # id, ctx.
            self.cb_connection_created[connection_id].append(func)
            return func

        return wrapper

    def register_on_disconnect(self, connection_id: str):
        def wrapper(func: Callable[[str], None]):
            self.cb_connection_destroyed[connection_id].append(func)
            return func

        return wrapper

    def register_on_data_received(self, connection_id: str):
        def wrapper(func: Callable[["Service", str, OriginProvider[bytes]], None]):
            self.cb_data_received[connection_id].append(func)
            return func

        return wrapper
