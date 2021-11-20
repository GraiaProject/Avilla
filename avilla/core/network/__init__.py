from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from .service import Service
    from .policy import Policy
    from .schema import Schema
    from .activity import Activity
    from avilla.core.network.partition import PartitionSymbol

TMetadata = TypeVar("TMetadata", bound="Schema")
TPolicy = TypeVar("TPolicy", bound="Policy")
TService = TypeVar("TService", bound="Service")
TActivity = TypeVar("TActivity", bound="Activity")
TPartition = TypeVar("TPartition", bound="PartitionSymbol")
