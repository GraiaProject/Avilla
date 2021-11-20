from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import (
    Awaitable,
    Callable,
    ClassVar,
    Dict,
    TypeVar,
    Generic,
    Union,
    Type,
    Tuple,
    Any,
    cast,
)
from avilla.core.launch import LaunchComponent

from avilla.core.network.activity import Activity
from .partition import PartitionSymbol
from .endpoint import Endpoint
from . import TMetadata, TPartition, TPolicy, TService, TActivity


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


_C = TypeVar("_C")


TPartitionHandler = Callable[[PartitionSymbol], Awaitable[None]]
TActivityHandler = Callable[[Union[Type[Activity], Activity]], Awaitable[Any]]


class PolicyProtocol:
    endpoint: Endpoint
    partition_handlers: Dict[Type[PartitionSymbol], TPartitionHandler]
    activity_handlers: Dict[Type[Activity], TActivityHandler]

    def __init__(
        self,
        endpoint: Endpoint,
        partition_handlers: Dict[Type[PartitionSymbol], TPartitionHandler],
        activity_handlers: Dict[Type[Activity], TActivityHandler],
    ):
        self.endpoint = endpoint
        self.partition_handlers = partition_handlers
        self.activity_handlers = activity_handlers

    async def apply(self, *activities: Union[Activity, Type[Activity]]) -> None:
        for activity in activities:
            activity_class = type(activity) if isinstance(activity, Activity) else activity
            if activity_class not in self.activity_handlers:
                raise TypeError(f"No handler for {activity_class}")
            await self.activity_handlers[activity_class](activity)


class Service(Generic[TMetadata, TPolicy], metaclass=ABCMeta):
    """
    Abstract class for services
    """

    id: ClassVar[ServiceId] = ServiceId("org.graia", "avilla.core", ".special", "null")
    endpoints: Dict[TMetadata, Endpoint[TMetadata, TPolicy]]

    _connections: Dict[str, Any]
    _connection_broadcasted_handlers: Dict[
        str,
        Tuple[
            Dict[Type[PartitionSymbol], TPartitionHandler],  # Partition
            Dict[Type[Activity], TActivityHandler],  # Activity
        ],
    ]

    @abstractmethod
    def __init__(self) -> None:
        self.endpoints = {}
        self._connections = {}
        self._connection_broadcasted_handlers = {}

    @property
    @abstractmethod
    def launch_component(self) -> LaunchComponent:
        return LaunchComponent("", set(), self.launch_mainline)

    @abstractmethod
    def register_endpoint(self, schema: TMetadata, policy: TPolicy) -> Endpoint[TMetadata, TPolicy]:
        """
        Register a new endpoint for the service, need override and super().call.
        """
        endpoint: "Endpoint[TMetadata, TPolicy]" = Endpoint(schema, policy)  # type: ignore
        self.endpoints[schema] = endpoint
        return endpoint

    @abstractmethod
    def remove_endpoint(self, endpoint: Endpoint[TMetadata, TPolicy]) -> None:
        """
        Remove an endpoint, need override and super().call.
        """
        self.endpoints.pop(endpoint.metadata)

    async def call_policy(
        self,
        endpoint: Endpoint,
        policy_name: str,
        partition_handlers: Dict[Type[PartitionSymbol], TPartitionHandler],
        activity_handlers: Dict[Type[Activity], TActivityHandler],
    ) -> None:
        policy_callable = cast(
            Callable[[PolicyProtocol], Awaitable[Any]], getattr(endpoint.policy, policy_name)
        )
        await policy_callable(PolicyProtocol(endpoint, partition_handlers, activity_handlers))

    async def broadcast_handlers(
        self,
        connection_id: str,
        partition_handlers: Dict[Type[PartitionSymbol], TPartitionHandler],
        activity_handlers: Dict[Type[Activity], TActivityHandler],
    ) -> None:
        self._connection_broadcasted_handlers[connection_id] = (
            partition_handlers,
            activity_handlers,
        )

    @abstractmethod
    def create_connection_obj(self) -> str:
        """抽象层处建立一个新的连接(即使是 HTTP 这种单次应答也需要)"""

    @abstractmethod
    def destroy_connection_obj(self, connection_id: str) -> None:
        """将抽象连接移出抽象层"""
        self._connections.pop(connection_id)
        self._connection_broadcasted_handlers.pop(connection_id)

    async def launch_mainline(self):
        """LaunchComponent.task"""

    async def launch_prepare(self):
        """LaunchComponent.prepare"""

    async def launch_cleanup(self):
        """LaunchComponent.cleanup"""
