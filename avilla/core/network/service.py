from abc import ABCMeta, abstractmethod, abstractproperty
from dataclasses import dataclass
from typing import ClassVar, Dict, TypeVar, Generic, Union, Type, Tuple, Any
from avilla.core.launch import LaunchComponent

from avilla.core.network.activity import Activity
from .partition import PartitionSymbol
from .endpoint import Endpoint
from . import M, P, S, A


@dataclass
class ServiceId:
    publisher: str
    namespace: str
    protocol_name: str
    method: str

    @property
    def avilla_uri(self):
        return (
            f"avilla://service/{self.publisher}/{self.namespace}/{self.protocol_name}/{self.method}"
        )


class ActivityCommitter(Generic[S, A]):
    service: S
    activities: Tuple[Union[A, Type[A]], ...]

    _to: str

    def __init__(self, service: S, activities: Tuple[Union[A, Type[A]], ...]) -> None:
        self.service = service
        self.activities = activities

    def __await__(self):
        return self.__await_impl__().__await__()

    def to(self, target: str):
        self._to = target
        return self

    async def __await_impl__(self):
        for activity in self.activities:
            await self.service.apply_activity(self._to, activity)


_C = TypeVar("_C")


class Service(Generic[M, P], metaclass=ABCMeta):
    """
    Abstract class for services
    """

    id: ClassVar[ServiceId] = ServiceId("org.graia", "avilla.core", ".special", "null")
    endpoints: Dict[M, Endpoint[M, P]]

    _connections: Dict[str, Any]

    @abstractmethod
    def __init__(self) -> None:
        self.endpoints = {}
        self._connections = {}

    @abstractproperty
    def launch_component(self) -> LaunchComponent:
        return LaunchComponent("", set(), self.launch_mainline)

    @abstractmethod
    def register_endpoint(self, schema: M, policy: P) -> Endpoint[M, P]:
        """
        Register a new endpoint for the service, need override and super().call.
        """
        endpoint: "Endpoint[M, P]" = Endpoint(schema, policy)  # type: ignore
        self.endpoints[schema] = endpoint
        return endpoint

    @abstractmethod
    def remove_endpoint(self, endpoint: Endpoint[M, P]) -> None:
        """
        Remove an endpoint, need override and super().call.
        """
        self.endpoints.pop(endpoint.metadata)

    def apply(self, *activities: Union[Activity, Type[Activity]]) -> ActivityCommitter:
        return ActivityCommitter(self, activities)

    @abstractmethod
    async def apply_activity(
        self, connection: str, activity: Union[Activity, Type[Activity]]
    ) -> None:
        """
        对指定连接应用传入的活动
        """
        pass

    @abstractmethod
    async def get_partition(self, connection: str, partition_symbol: PartitionSymbol[_C]) -> _C:
        """
        获取指定连接的指定信息区
        """
        pass

    @abstractmethod
    def create_connection_obj(self) -> str:
        """抽象层处建立一个新的连接(即使是 HTTP 这种单次应答也需要)"""

    @abstractmethod
    def destroy_connection_obj(self, connection_id: str) -> None:
        """将抽象连接移出抽象层"""

    @abstractmethod
    async def launch_mainline(self):
        """LaunchComponent.task"""

    async def launch_prepare(self):
        """LaunchComponent.prepare"""

    async def launch_cleanup(self):
        """LaunchComponent.cleanup"""
