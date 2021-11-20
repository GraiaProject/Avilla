from avilla.core.network.partition import PartitionSymbol
from dataclasses import dataclass


class Read(PartitionSymbol[bytes]):
    pass


@dataclass
class GetHeader(PartitionSymbol[str]):
    key: str


@dataclass
class GetCookie(PartitionSymbol[str]):
    key: str
