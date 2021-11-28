from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from avilla.core.network.partition import PartitionSymbol

    from .activity import Activity
    from .policy import Policy
    from .schema import Schema
    from .service import Service

TMetadata = TypeVar("TMetadata", bound="Schema")
TPolicy = TypeVar("TPolicy", bound="Policy")
TService = TypeVar("TService", bound="Service")
TActivity = TypeVar("TActivity", bound="Activity")
TPartition = TypeVar("TPartition", bound="PartitionSymbol")
